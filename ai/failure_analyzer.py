"""
Root-cause analysis of failed tests with Claude.

Enabled with ``pytest --ai-analysis``. For each failed test the conftest hook
collects a ``FailureContext`` while the page is still open and this module asks
Claude for a structured ``FailureAnalysis`` that is attached to the Allure report.
"""

import base64
import json
import logging
import os
from dataclasses import dataclass
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from ai.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-5-5"


class FailureAnalysis(BaseModel):
    """Structured answer returned by Claude."""

    category: Literal["product_bug", "test_bug", "locator_changed", "timing_flakiness", "environment", "unknown"]
    summary: str = Field(description="One sentence a reviewer can read in the report list")
    root_cause: str = Field(description="What went wrong and why, grounded in the evidence")
    evidence: list[str] = Field(description="Quotes from the error, snapshot or test source that support the diagnosis")
    suggested_fix: str = Field(description="Concrete change to make (file, locator, assertion or wait)")
    confidence: Literal["low", "medium", "high"]

    def to_markdown(self) -> str:
        evidence = "\n".join(f"- {item}" for item in self.evidence)
        return (
            f"## {self.category} ({self.confidence} confidence)\n\n"
            f"**Summary:** {self.summary}\n\n"
            f"### Root cause\n{self.root_cause}\n\n"
            f"### Evidence\n{evidence}\n\n"
            f"### Suggested fix\n{self.suggested_fix}\n"
        )


@dataclass(frozen=True)
class FailureContext:
    """Everything captured about a failure at the moment it happened."""

    test_id: str
    test_source: str
    error: str
    url: str | None = None
    aria_snapshot: str | None = None
    screenshot_jpeg: bytes | None = None


class FailureAnalyzer:
    """Sends failure contexts to Claude, with a per-session budget.

    Never raises: any API problem is logged and returned as ``None`` so the
    analysis can't hide or alter the real test result.
    """

    def __init__(
        self,
        client: anthropic.Anthropic | None = None,
        model: str | None = None,
        effort: str | None = None,
        max_analyses: int | None = None,
    ):
        self._client = client
        self.model = model or os.getenv("AI_ANALYSIS_MODEL", DEFAULT_MODEL)
        self.effort = effort or os.getenv("AI_ANALYSIS_EFFORT", "medium")
        self.max_analyses = max_analyses if max_analyses is not None else int(os.getenv("AI_ANALYSIS_MAX", "10"))
        self.analyses_done = 0
        self.disabled_reason: str | None = None

    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    def can_analyze(self) -> bool:
        return self.disabled_reason is None and self.analyses_done < self.max_analyses

    def analyze(self, context: FailureContext) -> FailureAnalysis | None:
        if not self.can_analyze():
            return None
        self.analyses_done += 1

        try:
            response = self.client.beta.messages.parse(
                model=self.model,
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                cache_control={"type": "ephemeral"},
                output_config={"effort": self.effort},
                output_format=FailureAnalysis,
                # On a safety-classifier decline, re-run on Anthropic's recommended fallback model.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                messages=[{"role": "user", "content": self._build_content(context)}],
            )
        except anthropic.AuthenticationError:
            self.disabled_reason = "No valid Anthropic credentials (set ANTHROPIC_API_KEY)"
            logger.warning("AI analysis disabled: %s", self.disabled_reason)
            return None
        except anthropic.RateLimitError:
            logger.warning("AI analysis rate limited for %s", context.test_id)
            return None
        except anthropic.APIStatusError as error:
            logger.warning("AI analysis failed for %s: HTTP %s %s", context.test_id, error.status_code, error.message)
            return None
        except anthropic.APIConnectionError as error:
            logger.warning("AI analysis could not reach the API for %s: %s", context.test_id, error)
            return None
        except Exception as error:  # e.g. no credentials configured: reporting must never break the run
            self.disabled_reason = f"{type(error).__name__}: {error}"
            logger.warning("AI analysis disabled: %s", self.disabled_reason)
            return None

        if response.stop_reason == "refusal":
            logger.warning("AI analysis declined for %s", context.test_id)
            return None
        logger.info(
            "AI analysis for %s: %s input (%s cached), %s output tokens",
            context.test_id,
            response.usage.input_tokens,
            response.usage.cache_read_input_tokens,
            response.usage.output_tokens,
        )
        return response.parsed_output

    @staticmethod
    def _build_content(context: FailureContext) -> list[dict]:
        content: list[dict] = []
        if context.screenshot_jpeg:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64.standard_b64encode(context.screenshot_jpeg).decode("ascii"),
                    },
                }
            )
        sections = {
            "test_id": context.test_id,
            "test_source": context.test_source,
            "error": context.error,
            "page_url": context.url or "(no page)",
            "aria_snapshot": context.aria_snapshot or "(not available)",
        }
        text = "\n\n".join(f"<{name}>\n{value}\n</{name}>" for name, value in sections.items())
        content.append({"type": "text", "text": text + "\n\nDiagnose this failure."})
        return content


def analysis_to_json(analysis: FailureAnalysis) -> str:
    return json.dumps(analysis.model_dump(), indent=2, ensure_ascii=False)

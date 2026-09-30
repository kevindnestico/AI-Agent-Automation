"""
Unit tests for the Claude failure analyzer, using a fake client (no API calls, no browser).
"""

from types import SimpleNamespace

import anthropic
import httpx2
import pytest

from ai.failure_analyzer import FailureAnalysis, FailureAnalyzer, FailureContext

pytestmark = pytest.mark.unit

ANALYSIS = FailureAnalysis(
    category="locator_changed",
    summary="Checkout button data-test was renamed",
    root_cause="get_by_test_id('checkout') matches nothing; snapshot shows button 'Proceed'.",
    evidence=['waiting for get_by_test_id("checkout")'],
    suggested_fix="Update CartPage.checkout_button locator.",
    confidence="high",
)
CONTEXT = FailureContext(
    test_id="tests/test_cart.py::test_x",
    test_source="def test_x(): ...",
    error="AssertionError: Locator expected to be visible",
    url="https://www.saucedemo.com/cart.html",
    aria_snapshot='- button "Proceed"',
    screenshot_jpeg=b"\xff\xd8fake-jpeg",
)


class FakeMessages:
    def __init__(self, result=None, error: Exception | None = None):
        self.calls: list[dict] = []
        self._result = result
        self._error = error

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        if self._error:
            raise self._error
        return self._result


def fake_client(messages: FakeMessages) -> anthropic.Anthropic:
    return SimpleNamespace(beta=SimpleNamespace(messages=messages))  # type: ignore[return-value]


def ok_response(stop_reason: str = "end_turn"):
    usage = SimpleNamespace(input_tokens=1200, cache_read_input_tokens=900, output_tokens=300)
    return SimpleNamespace(stop_reason=stop_reason, parsed_output=ANALYSIS, usage=usage)


def api_error(cls: type[anthropic.APIStatusError], status: int) -> anthropic.APIStatusError:
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    return cls("error", response=httpx2.Response(status, request=request), body=None)


def test_returns_structured_analysis_and_sends_full_context():
    messages = FakeMessages(ok_response())
    analyzer = FailureAnalyzer(client=fake_client(messages), model="claude-opus-5-5", effort="medium")

    assert analyzer.analyze(CONTEXT) == ANALYSIS

    request = messages.calls[0]
    assert request["model"] == "claude-opus-5-5"
    assert request["output_format"] is FailureAnalysis
    assert request["output_config"] == {"effort": "medium"}
    assert request["cache_control"] == {"type": "ephemeral"}
    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert "<aria_snapshot>" in content[1]["text"]
    assert CONTEXT.error in content[1]["text"]


def test_system_prompt_is_static_for_prompt_caching():
    messages = FakeMessages(ok_response())
    analyzer = FailureAnalyzer(client=fake_client(messages))

    analyzer.analyze(CONTEXT)
    analyzer.analyze(FailureContext(test_id="other", test_source="", error="boom"))

    assert messages.calls[0]["system"] == messages.calls[1]["system"]


def test_stops_after_session_budget():
    messages = FakeMessages(ok_response())
    analyzer = FailureAnalyzer(client=fake_client(messages), max_analyses=2)

    results = [analyzer.analyze(CONTEXT) for _ in range(3)]

    assert results[2] is None
    assert len(messages.calls) == 2


def test_refusal_returns_none():
    analyzer = FailureAnalyzer(client=fake_client(FakeMessages(ok_response(stop_reason="refusal"))))

    assert analyzer.analyze(CONTEXT) is None


def test_authentication_error_disables_analyzer():
    messages = FakeMessages(error=api_error(anthropic.AuthenticationError, 401))
    analyzer = FailureAnalyzer(client=fake_client(messages))

    assert analyzer.analyze(CONTEXT) is None
    assert analyzer.disabled_reason
    assert analyzer.analyze(CONTEXT) is None
    assert len(messages.calls) == 1, "No further calls after an auth failure"


def test_transient_errors_do_not_disable_analyzer():
    messages = FakeMessages(error=api_error(anthropic.InternalServerError, 500))
    analyzer = FailureAnalyzer(client=fake_client(messages))

    assert analyzer.analyze(CONTEXT) is None
    assert analyzer.can_analyze()


def test_markdown_report_contains_all_sections():
    markdown = ANALYSIS.to_markdown()

    for fragment in ("locator_changed", "high confidence", "Root cause", "Evidence", "Suggested fix"):
        assert fragment in markdown

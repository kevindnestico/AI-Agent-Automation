"""
Centralized test configuration.

Values are read from environment variables (or a local ``.env`` file) so the
same suite can run against different environments without code changes.
The base URL is handled by pytest-base-url (``--base-url`` / ``base_url`` in pytest.ini).
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings for the test suite."""

    password: str = os.getenv("SAUCE_PASSWORD", "secret_sauce")
    tax_rate: float = float(os.getenv("SAUCE_TAX_RATE", "0.08"))
    expect_timeout_ms: int = int(os.getenv("EXPECT_TIMEOUT_MS", "5000"))
    slow_login_timeout_ms: int = int(os.getenv("SLOW_LOGIN_TIMEOUT_MS", "15000"))
    # Saucedemo's session cookie lives 10 minutes; refresh cached auth before that.
    auth_state_ttl_seconds: int = int(os.getenv("AUTH_STATE_TTL_SECONDS", "480"))


settings = Settings()

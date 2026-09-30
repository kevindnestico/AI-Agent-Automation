"""
Base Page class with common functionality for all page objects.
"""
import re
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.components.header import Header


def parse_price(text: str) -> float:
    """Extract the numeric amount from strings like ``"$29.99"`` or ``"Tax: $2.40"``."""
    return float(text.rsplit("$", 1)[1])


class BasePage:
    """Base class for all page objects.

    Subclasses declare ``PATH`` (relative to ``base_url``) and optionally ``TITLE``
    (text of the secondary header). ``should_be_loaded`` waits for both, which
    guarantees the React view has rendered before any data is read from it.
    """

    PATH: str = "/"
    TITLE: str | None = None

    def __init__(self, page: Page):
        """
        Initialize the base page.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.header = Header(page)
        self._title: Locator = page.get_by_test_id("title")

    def open(self) -> Self:
        """Navigate directly to this page and wait until it is loaded."""
        with allure.step(f"Open {type(self).__name__} ({self.PATH})"):
            self.page.goto(self.PATH)
            return self.should_be_loaded()

    def should_be_loaded(self) -> Self:
        """Assert the browser is on this page and its content has rendered."""
        expect(self.page).to_have_url(re.compile(re.escape(self.PATH) + r"(\?.*)?$"))
        if self.TITLE:
            expect(self._title).to_have_text(self.TITLE)
        return self

    @property
    def url(self) -> str:
        """Current page URL."""
        return self.page.url

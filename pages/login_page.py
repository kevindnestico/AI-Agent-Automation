"""
Login Page Object Model for Saucedemo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import allure
from playwright.sync_api import Locator, Page, expect

from config import settings
from data.users import User
from pages.base_page import BasePage

if TYPE_CHECKING:
    from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    """Page object for the Saucedemo login page."""

    PATH = "/"

    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input: Locator = page.get_by_test_id("username")
        self.password_input: Locator = page.get_by_test_id("password")
        self.login_button: Locator = page.get_by_test_id("login-button")
        self.error_message: Locator = page.get_by_test_id("error")

    def should_be_loaded(self) -> Self:
        super().should_be_loaded()
        expect(self.login_button).to_be_visible()
        return self

    @allure.step("Submit login form as {username}")
    def login(self, username: str, password: str) -> None:
        """Fill and submit the login form without asserting the outcome."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def login_as(self, user: User, timeout: float | None = None) -> InventoryPage:
        """Log in with a valid account and return the loaded inventory page.

        Args:
            user: Account to log in with.
            timeout: Max time (ms) to wait for the inventory page. Defaults to a
                longer timeout for ``performance_glitch_user``.
        """
        from pages.inventory_page import InventoryPage

        self.login(user, settings.password)
        if timeout is None and user is User.PERFORMANCE_GLITCH:
            timeout = settings.slow_login_timeout_ms
        inventory = InventoryPage(self.page)
        expect(inventory.inventory_list).to_be_visible(timeout=timeout)
        return inventory.should_be_loaded()

    def get_error_message(self) -> str:
        expect(self.error_message).to_be_visible()
        return self.error_message.inner_text()

    def should_show_error(self, message: str) -> None:
        expect(self.error_message).to_have_text(message)

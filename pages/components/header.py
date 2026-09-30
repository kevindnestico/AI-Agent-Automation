"""
Header component shared by every authenticated page (cart icon + burger menu).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import allure
from playwright.sync_api import Locator, Page, expect

if TYPE_CHECKING:
    from pages.cart_page import CartPage
    from pages.inventory_page import InventoryPage
    from pages.login_page import LoginPage


class Header:
    """Primary header: shopping cart link/badge and the side menu."""

    def __init__(self, page: Page):
        self.page = page
        self.cart_link: Locator = page.get_by_test_id("shopping-cart-link")
        self.cart_badge: Locator = page.get_by_test_id("shopping-cart-badge")
        self._open_menu: Locator = page.get_by_role("button", name="Open Menu")
        self._close_menu: Locator = page.get_by_role("button", name="Close Menu")
        self._all_items_link: Locator = page.get_by_test_id("inventory-sidebar-link")
        self._logout_link: Locator = page.get_by_test_id("logout-sidebar-link")
        self._reset_link: Locator = page.get_by_test_id("reset-sidebar-link")

    def cart_count(self) -> int:
        """Number shown in the cart badge (0 when the badge is hidden)."""
        return int(self.cart_badge.inner_text()) if self.cart_badge.is_visible() else 0

    def should_have_cart_count(self, count: int) -> None:
        """Assert the cart badge value, waiting for the UI to update."""
        if count == 0:
            expect(self.cart_badge).to_be_hidden()
        else:
            expect(self.cart_badge).to_have_text(str(count))

    @allure.step("Open cart")
    def open_cart(self) -> CartPage:
        from pages.cart_page import CartPage

        self.cart_link.click()
        return CartPage(self.page).should_be_loaded()

    def open_menu(self) -> None:
        self._open_menu.click()
        expect(self._logout_link).to_be_visible()

    def close_menu(self) -> None:
        self._close_menu.click()
        expect(self._logout_link).to_be_hidden()

    @allure.step("Log out")
    def logout(self) -> LoginPage:
        from pages.login_page import LoginPage

        self.open_menu()
        self._logout_link.click()
        return LoginPage(self.page).should_be_loaded()

    @allure.step("Reset app state")
    def reset_app_state(self) -> None:
        self.open_menu()
        self._reset_link.click()
        self.close_menu()

    @allure.step("Go to all items")
    def go_to_all_items(self) -> InventoryPage:
        from pages.inventory_page import InventoryPage

        self.open_menu()
        self._all_items_link.click()
        return InventoryPage(self.page).should_be_loaded()

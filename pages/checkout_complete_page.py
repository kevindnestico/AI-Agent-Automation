"""
Checkout Complete Page Object Model for Saucedemo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import allure
from playwright.sync_api import Locator, Page, expect

from data.messages import ORDER_COMPLETE_HEADER
from pages.base_page import BasePage

if TYPE_CHECKING:
    from pages.inventory_page import InventoryPage


class CheckoutCompletePage(BasePage):
    """Page object for the order confirmation page."""

    PATH = "/checkout-complete.html"
    TITLE = "Checkout: Complete!"

    def __init__(self, page: Page):
        super().__init__(page)
        self.complete_header: Locator = page.get_by_test_id("complete-header")
        self.complete_text: Locator = page.get_by_test_id("complete-text")
        self.success_image: Locator = page.get_by_test_id("pony-express")
        self.back_home_button: Locator = page.get_by_test_id("back-to-products")

    def should_show_order_confirmation(self) -> None:
        expect(self.complete_header).to_have_text(ORDER_COMPLETE_HEADER)
        expect(self.complete_text).to_be_visible()
        expect(self.success_image).to_be_visible()

    @allure.step("Back home")
    def back_home(self) -> InventoryPage:
        from pages.inventory_page import InventoryPage

        self.back_home_button.click()
        return InventoryPage(self.page).should_be_loaded()

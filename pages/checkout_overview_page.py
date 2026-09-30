"""
Checkout Overview Page Object Model for Saucedemo.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import allure
from playwright.sync_api import Locator, Page

from pages.base_page import BasePage, parse_price

if TYPE_CHECKING:
    from pages.checkout_complete_page import CheckoutCompletePage
    from pages.inventory_page import InventoryPage


@dataclass(frozen=True)
class PaymentSummary:
    subtotal: float
    tax: float
    total: float


class CheckoutOverviewPage(BasePage):
    """Page object for checkout step two (order overview)."""

    PATH = "/checkout-step-two.html"
    TITLE = "Checkout: Overview"

    def __init__(self, page: Page):
        super().__init__(page)
        self.items: Locator = page.get_by_test_id("inventory-item")
        self.item_names: Locator = page.get_by_test_id("inventory-item-name")
        self.item_prices: Locator = page.get_by_test_id("inventory-item-price")
        self.payment_info: Locator = page.get_by_test_id("payment-info-value")
        self.shipping_info: Locator = page.get_by_test_id("shipping-info-value")
        self.subtotal_label: Locator = page.get_by_test_id("subtotal-label")
        self.tax_label: Locator = page.get_by_test_id("tax-label")
        self.total_label: Locator = page.get_by_test_id("total-label")
        self.finish_button: Locator = page.get_by_test_id("finish")
        self.cancel_button: Locator = page.get_by_test_id("cancel")

    def click_finish(self) -> None:
        """Click Finish without asserting the outcome."""
        self.finish_button.click()

    @allure.step("Finish order")
    def finish(self) -> CheckoutCompletePage:
        from pages.checkout_complete_page import CheckoutCompletePage

        self.click_finish()
        return CheckoutCompletePage(self.page).should_be_loaded()

    @allure.step("Cancel from overview")
    def cancel(self) -> InventoryPage:
        from pages.inventory_page import InventoryPage

        self.cancel_button.click()
        return InventoryPage(self.page).should_be_loaded()

    def get_payment_summary(self) -> PaymentSummary:
        return PaymentSummary(
            subtotal=parse_price(self.subtotal_label.inner_text()),
            tax=parse_price(self.tax_label.inner_text()),
            total=parse_price(self.total_label.inner_text()),
        )

    def get_item_count(self) -> int:
        return self.items.count()

    def get_item_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def get_item_prices(self) -> list[float]:
        return [parse_price(text) for text in self.item_prices.all_inner_texts()]

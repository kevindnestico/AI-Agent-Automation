"""
Checkout Information Page Object Model for Saucedemo.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Self

import allure
from playwright.sync_api import Locator, Page, expect

from data.customers import Customer
from pages.base_page import BasePage

if TYPE_CHECKING:
    from pages.cart_page import CartPage
    from pages.checkout_overview_page import CheckoutOverviewPage


class CheckoutInfoPage(BasePage):
    """Page object for checkout step one (customer information)."""

    PATH = "/checkout-step-one.html"
    TITLE = "Checkout: Your Information"

    def __init__(self, page: Page):
        super().__init__(page)
        self.first_name_input: Locator = page.get_by_test_id("firstName")
        self.last_name_input: Locator = page.get_by_test_id("lastName")
        self.postal_code_input: Locator = page.get_by_test_id("postalCode")
        self.continue_button: Locator = page.get_by_test_id("continue")
        self.cancel_button: Locator = page.get_by_test_id("cancel")
        self.error_message: Locator = page.get_by_test_id("error")

    @allure.step("Fill customer info: {first_name} {last_name}, {postal_code}")
    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> Self:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)
        return self

    def fill_customer(self, customer: Customer) -> Self:
        return self.fill_info(customer.first_name, customer.last_name, customer.postal_code)

    def submit(self) -> None:
        """Click Continue without asserting the outcome (for negative tests)."""
        self.continue_button.click()

    @allure.step("Continue to overview")
    def continue_to_overview(self) -> CheckoutOverviewPage:
        from pages.checkout_overview_page import CheckoutOverviewPage

        self.submit()
        return CheckoutOverviewPage(self.page).should_be_loaded()

    @allure.step("Cancel checkout")
    def cancel(self) -> CartPage:
        from pages.cart_page import CartPage

        self.cancel_button.click()
        return CartPage(self.page).should_be_loaded()

    def get_field_values(self) -> tuple[str, str, str]:
        return (
            self.first_name_input.input_value(),
            self.last_name_input.input_value(),
            self.postal_code_input.input_value(),
        )

    def should_show_error(self, message: str) -> None:
        expect(self.error_message).to_have_text(message)

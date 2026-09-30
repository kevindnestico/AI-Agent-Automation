"""
Cart Page Object Model for Saucedemo.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Self

import allure
from playwright.sync_api import Locator, Page, expect

from data.products import Product
from pages.base_page import BasePage, parse_price

if TYPE_CHECKING:
    from pages.checkout_info_page import CheckoutInfoPage
    from pages.inventory_page import InventoryPage


class CartPage(BasePage):
    """Page object for the Saucedemo shopping cart page."""

    PATH = "/cart.html"
    TITLE = "Your Cart"

    def __init__(self, page: Page):
        super().__init__(page)
        self.items: Locator = page.get_by_test_id("inventory-item")
        self.item_names: Locator = page.get_by_test_id("inventory-item-name")
        self.item_prices: Locator = page.get_by_test_id("inventory-item-price")
        self.checkout_button: Locator = page.get_by_test_id("checkout")
        self.continue_shopping_button: Locator = page.get_by_test_id("continue-shopping")

    @allure.step("Remove {product} from cart page")
    def remove(self, product: Product) -> Self:
        item = self.items.filter(has_text=product.name)
        self.page.get_by_test_id(f"remove-{product.slug}").click()
        expect(item).to_have_count(0)
        return self

    @allure.step("Proceed to checkout")
    def checkout(self) -> CheckoutInfoPage:
        from pages.checkout_info_page import CheckoutInfoPage

        self.checkout_button.click()
        return CheckoutInfoPage(self.page).should_be_loaded()

    @allure.step("Continue shopping")
    def continue_shopping(self) -> InventoryPage:
        from pages.inventory_page import InventoryPage

        self.continue_shopping_button.click()
        return InventoryPage(self.page).should_be_loaded()

    def should_contain(self, *products: Product) -> None:
        """Assert the cart contains exactly the given products (any order)."""
        expect(self.items).to_have_count(len(products))
        assert sorted(self.get_item_names()) == sorted(p.name for p in products)

    def get_item_count(self) -> int:
        return self.items.count()

    def get_item_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def get_item_prices(self) -> list[float]:
        return [parse_price(text) for text in self.item_prices.all_inner_texts()]

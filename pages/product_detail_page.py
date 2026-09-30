"""
Product Detail Page Object Model for Saucedemo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage, parse_price

if TYPE_CHECKING:
    from pages.inventory_page import InventoryPage


class ProductDetailPage(BasePage):
    """Page object for ``/inventory-item.html?id=<id>``."""

    PATH = "/inventory-item.html"

    def __init__(self, page: Page):
        super().__init__(page)
        self.name: Locator = page.get_by_test_id("inventory-item-name")
        self.description: Locator = page.get_by_test_id("inventory-item-desc")
        self.price: Locator = page.get_by_test_id("inventory-item-price")
        self.add_to_cart_button: Locator = page.get_by_test_id("add-to-cart")
        self.remove_button: Locator = page.get_by_test_id("remove")
        self.back_button: Locator = page.get_by_test_id("back-to-products")

    def should_be_loaded(self) -> Self:
        super().should_be_loaded()
        # The URL changes before React swaps the view; wait for a detail-only element.
        expect(self.back_button).to_be_visible()
        expect(self.name).to_be_visible()
        return self

    def get_price(self) -> float:
        return parse_price(self.price.inner_text())

    @allure.step("Add product to cart from detail page")
    def add_to_cart(self) -> Self:
        self.add_to_cart_button.click()
        expect(self.remove_button).to_be_visible()
        return self

    @allure.step("Remove product from detail page")
    def remove_from_cart(self) -> Self:
        self.remove_button.click()
        expect(self.add_to_cart_button).to_be_visible()
        return self

    @allure.step("Back to products")
    def back_to_products(self) -> InventoryPage:
        from pages.inventory_page import InventoryPage

        self.back_button.click()
        return InventoryPage(self.page).should_be_loaded()

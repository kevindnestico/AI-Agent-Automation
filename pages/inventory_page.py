"""
Inventory Page Object Model for Saucedemo.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Self

import allure
from playwright.sync_api import Locator, Page, expect

from data.products import Product, SortOption
from pages.base_page import BasePage, parse_price

if TYPE_CHECKING:
    from pages.cart_page import CartPage
    from pages.product_detail_page import ProductDetailPage


class InventoryPage(BasePage):
    """Page object for the Saucedemo inventory/products page."""

    PATH = "/inventory.html"
    TITLE = "Products"

    def __init__(self, page: Page):
        super().__init__(page)
        self.inventory_list: Locator = page.get_by_test_id("inventory-list")
        self.items: Locator = page.get_by_test_id("inventory-item")
        self.item_names: Locator = page.get_by_test_id("inventory-item-name")
        self.item_prices: Locator = page.get_by_test_id("inventory-item-price")
        self.item_images: Locator = page.locator("img.inventory_item_img")
        self.sort_select: Locator = page.get_by_test_id("product-sort-container")

    def add_to_cart_button(self, product: Product) -> Locator:
        return self.page.get_by_test_id(f"add-to-cart-{product.slug}")

    def remove_button(self, product: Product) -> Locator:
        return self.page.get_by_test_id(f"remove-{product.slug}")

    @allure.step("Add {product} to cart")
    def add_to_cart(self, product: Product) -> Self:
        """Add a product and verify its button toggles to "Remove"."""
        self.add_to_cart_button(product).click()
        expect(self.remove_button(product)).to_be_visible()
        return self

    def add_products(self, *products: Product) -> Self:
        for product in products:
            self.add_to_cart(product)
        return self

    @allure.step("Remove {product} from cart")
    def remove_from_cart(self, product: Product) -> Self:
        """Remove a product and verify its button toggles back to "Add to cart"."""
        self.remove_button(product).click()
        expect(self.add_to_cart_button(product)).to_be_visible()
        return self

    def sort_by(self, option: SortOption) -> Self:
        with allure.step(f"Sort products by {option.name}"):
            self.sort_select.select_option(option.value)
        return self

    @allure.step("Open product {product}")
    def open_product(self, product: Product) -> ProductDetailPage:
        from pages.product_detail_page import ProductDetailPage

        self.item_names.filter(has_text=product.name).click()
        return ProductDetailPage(self.page).should_be_loaded()

    def go_to_cart(self) -> CartPage:
        return self.header.open_cart()

    def get_product_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def get_product_prices(self) -> list[float]:
        return [parse_price(text) for text in self.item_prices.all_inner_texts()]

    def get_image_sources(self) -> list[str]:
        return self.item_images.evaluate_all("imgs => imgs.map(img => img.getAttribute('src'))")

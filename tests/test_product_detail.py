"""
Product detail page tests.
"""

import allure
import pytest

from data.products import ALL_PRODUCTS, BACKPACK, Product
from pages import InventoryPage, ProductDetailPage

pytestmark = allure.feature("Product detail")


@pytest.mark.parametrize("product", ALL_PRODUCTS, ids=lambda p: p.slug)
def test_product_detail_matches_catalog(inventory_page: InventoryPage, product: Product):
    detail = inventory_page.open_product(product)

    assert detail.name.inner_text() == product.name
    assert detail.get_price() == product.price
    assert detail.description.inner_text().strip(), "Description should not be empty"
    assert f"id={product.id}" in detail.url


@pytest.mark.smoke
def test_add_to_cart_from_detail_page(inventory_page: InventoryPage):
    detail = inventory_page.open_product(BACKPACK).add_to_cart()
    detail.header.should_have_cart_count(1)

    detail.header.open_cart().should_contain(BACKPACK)


def test_remove_from_detail_page(inventory_page: InventoryPage):
    detail = inventory_page.open_product(BACKPACK).add_to_cart()

    detail.remove_from_cart()

    detail.header.should_have_cart_count(0)


def test_cart_state_shared_between_detail_and_inventory(inventory_page: InventoryPage):
    inventory = inventory_page.open_product(BACKPACK).add_to_cart().back_to_products()

    inventory.header.should_have_cart_count(1)
    inventory.remove_button(BACKPACK).wait_for()


def test_detail_page_direct_link(inventory_page: InventoryPage):
    page = inventory_page.page
    page.goto(f"{ProductDetailPage.PATH}?id={BACKPACK.id}")

    assert ProductDetailPage(page).should_be_loaded().name.inner_text() == BACKPACK.name

"""
Inventory (products page) tests for Saucedemo.
"""
import allure
import pytest

from data.products import ALL_PRODUCTS, BACKPACK, BIKE_LIGHT, BOLT_T_SHIRT, SortOption
from pages import InventoryPage

pytestmark = allure.feature("Inventory")


@pytest.mark.smoke
def test_add_single_item_to_cart(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK)

    inventory_page.header.should_have_cart_count(1)


@pytest.mark.smoke
def test_add_multiple_items_to_cart(inventory_page: InventoryPage):
    inventory_page.add_products(BACKPACK, BIKE_LIGHT, BOLT_T_SHIRT)

    inventory_page.header.should_have_cart_count(3)


def test_remove_item_from_inventory(inventory_page: InventoryPage):
    inventory_page.add_products(BACKPACK, BIKE_LIGHT)

    inventory_page.remove_from_cart(BACKPACK)

    inventory_page.header.should_have_cart_count(1)


def test_add_all_items_to_cart(inventory_page: InventoryPage):
    inventory_page.add_products(*ALL_PRODUCTS)

    inventory_page.header.should_have_cart_count(len(ALL_PRODUCTS))


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("option", "key", "reverse"),
    [
        pytest.param(SortOption.PRICE_LOW_TO_HIGH, "price", False, id="price-low-to-high"),
        pytest.param(SortOption.PRICE_HIGH_TO_LOW, "price", True, id="price-high-to-low"),
        pytest.param(SortOption.NAME_A_TO_Z, "name", False, id="name-a-to-z"),
        pytest.param(SortOption.NAME_Z_TO_A, "name", True, id="name-z-to-a"),
    ],
)
def test_sort_products(inventory_page: InventoryPage, option: SortOption, key: str, reverse: bool):
    inventory_page.sort_by(option)

    values = inventory_page.get_product_prices() if key == "price" else inventory_page.get_product_names()
    assert values == sorted(values, reverse=reverse), f"Products not sorted by {option.name}: {values}"


@pytest.mark.regression
def test_inventory_matches_catalog(inventory_page: InventoryPage):
    names = inventory_page.get_product_names()
    prices = inventory_page.get_product_prices()

    assert dict(zip(names, prices)) == {p.name: p.price for p in ALL_PRODUCTS}


@pytest.mark.regression
def test_all_products_have_valid_prices(inventory_page: InventoryPage):
    prices = inventory_page.get_product_prices()

    assert len(prices) == len(ALL_PRODUCTS)
    assert all(price > 0 for price in prices), f"Found non-positive prices: {prices}"


def test_navigate_to_cart_from_inventory(inventory_page: InventoryPage):
    cart = inventory_page.go_to_cart()

    cart.should_contain()

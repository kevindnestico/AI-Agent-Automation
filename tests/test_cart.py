"""
Shopping cart functionality tests for Saucedemo.
"""
import allure
import pytest

from data.products import BACKPACK, BIKE_LIGHT
from pages import CartPage, InventoryPage

pytestmark = allure.feature("Cart")


@pytest.mark.smoke
def test_cart_displays_added_items(cart_page: CartPage):
    cart_page.should_contain(BACKPACK, BIKE_LIGHT)


@pytest.mark.smoke
def test_remove_item_from_cart(cart_page: CartPage):
    cart_page.remove(BACKPACK)

    cart_page.should_contain(BIKE_LIGHT)
    cart_page.header.should_have_cart_count(1)


def test_remove_all_items_from_cart(cart_page: CartPage):
    cart_page.remove(BACKPACK).remove(BIKE_LIGHT)

    cart_page.should_contain()
    cart_page.header.should_have_cart_count(0)


@pytest.mark.smoke
def test_continue_shopping_from_cart(cart_page: CartPage):
    inventory = cart_page.continue_shopping()

    inventory.header.should_have_cart_count(2)


@pytest.mark.smoke
def test_proceed_to_checkout_from_cart(cart_page: CartPage):
    cart_page.checkout().should_be_loaded()


def test_cart_item_prices_match_catalog(cart_page: CartPage):
    assert sorted(cart_page.get_item_prices()) == sorted([BACKPACK.price, BIKE_LIGHT.price])


def test_empty_cart(inventory_page: InventoryPage):
    cart = inventory_page.go_to_cart()

    cart.should_contain()
    cart.header.should_have_cart_count(0)


@pytest.mark.regression
def test_cart_persists_items_after_navigation(inventory_page: InventoryPage):
    """Items added through the UI survive navigating away from and back to the cart."""
    cart = inventory_page.add_to_cart(BACKPACK).go_to_cart()
    cart.should_contain(BACKPACK)

    cart = cart.continue_shopping().go_to_cart()

    cart.should_contain(BACKPACK)


def test_cart_badge_updates_after_removal(cart_page: CartPage):
    cart_page.header.should_have_cart_count(2)

    cart_page.remove(BIKE_LIGHT)

    cart_page.header.should_have_cart_count(1)

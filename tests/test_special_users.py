"""
Behavior checks run for every login-capable user.

Each test asserts the correct behavior; users with a known defect are marked as
strict xfail through the registry in ``data/known_bugs.py``.
"""

import allure
import pytest

from data import known_bugs
from data.customers import DEFAULT_CUSTOMER
from data.products import ALL_PRODUCTS, BACKPACK, SortOption
from pages import CartPage, InventoryPage

pytestmark = [allure.feature("Special users"), pytest.mark.regression]


@pytest.mark.parametrize("user", known_bugs.users_with_known_bugs(known_bugs.BROKEN_PRODUCT_IMAGES), indirect=True)
def test_product_images_are_valid(inventory_page: InventoryPage):
    sources = inventory_page.get_image_sources()

    broken = [src for src in sources if "sl-404" in src]
    assert not broken, f"{len(broken)} product image(s) use the 404 placeholder"
    assert len(set(sources)) == len(ALL_PRODUCTS), "Every product should have its own image"


@pytest.mark.parametrize("user", known_bugs.users_with_known_bugs(known_bugs.SORTING_BROKEN), indirect=True)
def test_sort_by_price_high_to_low(inventory_page: InventoryPage):
    inventory_page.sort_by(SortOption.PRICE_HIGH_TO_LOW)

    prices = inventory_page.get_product_prices()
    assert prices == sorted(prices, reverse=True), f"Prices not sorted: {prices}"


@pytest.mark.parametrize("user", known_bugs.users_with_known_bugs(known_bugs.WRONG_PRICES), indirect=True)
def test_inventory_prices_match_catalog(inventory_page: InventoryPage):
    assert sorted(inventory_page.get_product_prices()) == sorted(p.price for p in ALL_PRODUCTS)


@pytest.mark.parametrize("user", known_bugs.users_with_known_bugs(known_bugs.CANNOT_ADD_SOME_PRODUCTS), indirect=True)
def test_every_product_can_be_added_to_cart(inventory_page: InventoryPage):
    inventory_page.add_products(*ALL_PRODUCTS)

    inventory_page.header.should_have_cart_count(len(ALL_PRODUCTS))


@pytest.mark.parametrize(
    "user", known_bugs.users_with_known_bugs(known_bugs.CANNOT_REMOVE_FROM_INVENTORY), indirect=True
)
def test_product_can_be_removed_from_inventory(inventory_page: InventoryPage):
    inventory_page.add_to_cart(BACKPACK)

    inventory_page.remove_from_cart(BACKPACK)

    inventory_page.header.should_have_cart_count(0)


@pytest.mark.parametrize(
    "user", known_bugs.users_with_known_bugs(known_bugs.CHECKOUT_FORM_CORRUPTS_INPUT), indirect=True
)
def test_checkout_form_keeps_entered_values(cart_page: CartPage):
    checkout = cart_page.checkout().fill_customer(DEFAULT_CUSTOMER)

    assert checkout.get_field_values() == (
        DEFAULT_CUSTOMER.first_name,
        DEFAULT_CUSTOMER.last_name,
        DEFAULT_CUSTOMER.postal_code,
    )


@pytest.mark.parametrize(
    "user",
    known_bugs.users_with_known_bugs(
        known_bugs.CHECKOUT_FORM_CORRUPTS_INPUT,
        known_bugs.FINISH_DOES_NOT_COMPLETE_ORDER,
    ),
    indirect=True,
)
@pytest.mark.parametrize("cart_products", [(BACKPACK,)], ids=["backpack"])
def test_order_can_be_completed(cart_page: CartPage):
    overview = cart_page.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview()

    overview.finish().should_show_order_confirmation()

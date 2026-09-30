"""
End-to-end purchase flows for Saucedemo, driven entirely through the UI.
"""
import allure
import pytest

from data.customers import Customer, DEFAULT_CUSTOMER
from data.products import ALL_PRODUCTS, BACKPACK, BIKE_LIGHT, BOLT_T_SHIRT, FLEECE_JACKET, ONESIE, SortOption
from pages import InventoryPage

pytestmark = allure.feature("End-to-end purchase")


@pytest.mark.smoke
@pytest.mark.regression
def test_complete_purchase_single_item(inventory_page: InventoryPage):
    cart = inventory_page.add_to_cart(BACKPACK).go_to_cart()
    cart.should_contain(BACKPACK)

    overview = cart.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview()
    assert overview.get_item_names() == [BACKPACK.name]

    overview.finish().should_show_order_confirmation()


@pytest.mark.regression
def test_complete_purchase_multiple_items(inventory_page: InventoryPage):
    products = (BACKPACK, BIKE_LIGHT, BOLT_T_SHIRT, FLEECE_JACKET)
    cart = inventory_page.add_products(*products).go_to_cart()
    cart.should_contain(*products)

    overview = cart.checkout().fill_info("Maria", "Garcia", "90210").continue_to_overview()
    assert overview.get_item_count() == len(products)

    overview.finish().should_show_order_confirmation()


@pytest.mark.regression
def test_complete_purchase_all_items(inventory_page: InventoryPage):
    cart = inventory_page.add_products(*ALL_PRODUCTS).go_to_cart()
    cart.should_contain(*ALL_PRODUCTS)

    overview = cart.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview()

    overview.finish().should_show_order_confirmation()


def test_complete_purchase_with_item_removal(inventory_page: InventoryPage):
    cart = inventory_page.add_products(BACKPACK, BIKE_LIGHT, ONESIE).go_to_cart()

    cart.remove(BIKE_LIGHT)
    cart.should_contain(BACKPACK, ONESIE)

    overview = cart.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview()
    assert sorted(overview.get_item_names()) == sorted([BACKPACK.name, ONESIE.name])
    overview.finish().should_show_order_confirmation()


@pytest.mark.regression
def test_complete_purchase_with_international_characters(inventory_page: InventoryPage):
    cart = inventory_page.add_to_cart(ONESIE).go_to_cart()

    overview = cart.checkout().fill_customer(Customer("José", "Rodríguez", "28001")).continue_to_overview()

    overview.finish().should_show_order_confirmation()


@pytest.mark.regression
def test_complete_purchase_verify_payment_calculation(inventory_page: InventoryPage):
    cart = inventory_page.add_products(BACKPACK, BIKE_LIGHT).go_to_cart()
    expected_subtotal = round(sum(cart.get_item_prices()), 2)

    overview = cart.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview()
    summary = overview.get_payment_summary()

    assert summary.subtotal == pytest.approx(expected_subtotal)
    assert summary.tax > 0
    assert summary.total == pytest.approx(summary.subtotal + summary.tax)


def test_complete_purchase_return_to_inventory_after_completion(inventory_page: InventoryPage):
    cart = inventory_page.add_to_cart(BACKPACK).go_to_cart()
    complete = cart.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview().finish()

    inventory = complete.back_home()

    inventory.header.should_have_cart_count(0)


def test_complete_purchase_cheapest_item_after_sorting(inventory_page: InventoryPage):
    inventory_page.sort_by(SortOption.PRICE_LOW_TO_HIGH)
    cheapest = min(ALL_PRODUCTS, key=lambda product: product.price)
    assert inventory_page.get_product_names()[0] == cheapest.name

    cart = inventory_page.add_to_cart(cheapest).go_to_cart()
    overview = cart.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview()

    assert overview.get_payment_summary().subtotal == pytest.approx(cheapest.price)
    overview.finish().should_show_order_confirmation()

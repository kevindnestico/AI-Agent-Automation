"""
Order total calculations: subtotal, tax and total for different carts.
"""

import allure
import pytest

from config import settings
from data.products import ALL_PRODUCTS, BACKPACK, BIKE_LIGHT, FLEECE_JACKET, ONESIE, Product
from pages import CheckoutOverviewPage

pytestmark = allure.feature("Checkout calculations")


# Overrides the ``cart_products`` fixture used by cart_page -> checkout_overview_page.
@pytest.mark.regression
@pytest.mark.parametrize(
    "cart_products",
    [
        pytest.param((ONESIE,), id="cheapest-item"),
        pytest.param((FLEECE_JACKET,), id="most-expensive-item"),
        pytest.param((BACKPACK, BIKE_LIGHT), id="two-items"),
        pytest.param(ALL_PRODUCTS, id="all-items"),
    ],
)
def test_order_totals(checkout_overview_page: CheckoutOverviewPage, cart_products: tuple[Product, ...]):
    expected_subtotal = round(sum(product.price for product in cart_products), 2)
    expected_tax = round(expected_subtotal * settings.tax_rate, 2)

    summary = checkout_overview_page.get_payment_summary()

    assert sorted(checkout_overview_page.get_item_prices()) == sorted(p.price for p in cart_products)
    assert summary.subtotal == pytest.approx(expected_subtotal)
    assert summary.tax == pytest.approx(expected_tax, abs=0.01)
    assert summary.total == pytest.approx(summary.subtotal + summary.tax)

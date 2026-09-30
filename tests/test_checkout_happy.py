"""
Checkout happy path tests for Saucedemo.
"""

import allure
import pytest

from data.customers import DEFAULT_CUSTOMER
from data.products import BACKPACK, BIKE_LIGHT
from pages import CheckoutInfoPage, CheckoutOverviewPage

pytestmark = allure.feature("Checkout")


@pytest.mark.smoke
def test_checkout_happy_path(checkout_info_page: CheckoutInfoPage):
    overview = checkout_info_page.fill_customer(DEFAULT_CUSTOMER).continue_to_overview()

    assert sorted(overview.get_item_names()) == sorted([BACKPACK.name, BIKE_LIGHT.name])

    overview.finish().should_show_order_confirmation()


def test_overview_shows_payment_and_shipping_info(checkout_overview_page: CheckoutOverviewPage):
    assert checkout_overview_page.payment_info.inner_text().startswith("SauceCard #")
    assert checkout_overview_page.shipping_info.inner_text() == "Free Pony Express Delivery!"

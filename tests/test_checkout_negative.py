"""
Checkout negative and edge-case tests for Saucedemo.
"""
import allure
import pytest

from data.messages import CheckoutErrors
from pages import CheckoutInfoPage, CheckoutOverviewPage, InventoryPage

pytestmark = allure.feature("Checkout")


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "expected_error"),
    [
        pytest.param("", "Perez", "12345", CheckoutErrors.FIRST_NAME_REQUIRED, id="empty-first-name"),
        pytest.param("Juan", "", "12345", CheckoutErrors.LAST_NAME_REQUIRED, id="empty-last-name"),
        pytest.param("Juan", "Perez", "", CheckoutErrors.POSTAL_CODE_REQUIRED, id="empty-postal-code"),
        pytest.param("", "", "", CheckoutErrors.FIRST_NAME_REQUIRED, id="all-fields-empty"),
    ],
)
def test_checkout_required_fields(
    checkout_info_page: CheckoutInfoPage, first_name: str, last_name: str, postal_code: str, expected_error: str
):
    checkout_info_page.fill_info(first_name, last_name, postal_code).submit()

    checkout_info_page.should_show_error(expected_error)
    checkout_info_page.should_be_loaded()


def test_checkout_cancel_from_info_page(checkout_info_page: CheckoutInfoPage):
    cart = checkout_info_page.cancel()

    assert cart.get_item_count() == 2, "Cancelling checkout must keep the cart"


def test_checkout_cancel_from_overview_page(checkout_overview_page: CheckoutOverviewPage):
    inventory = checkout_overview_page.cancel()

    inventory.header.should_have_cart_count(2)


@pytest.mark.regression
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code"),
    [
        pytest.param("José-María", "O'Connor", "12345", id="special-characters"),
        pytest.param("A" * 100, "B" * 100, "1" * 20, id="very-long-values"),
        pytest.param("123", "456", "789", id="numeric-names"),
        pytest.param("Juan", "Perez", "ABCDE", id="alphabetic-postal-code"),
    ],
)
def test_checkout_accepts_unusual_input(
    checkout_info_page: CheckoutInfoPage, first_name: str, last_name: str, postal_code: str
):
    """Saucedemo performs no format validation; these inputs must reach the overview."""
    checkout_info_page.fill_info(first_name, last_name, postal_code).continue_to_overview()


def test_checkout_from_empty_cart(inventory_page: InventoryPage):
    """Saucedemo allows starting checkout with an empty cart (documented behavior)."""
    cart = inventory_page.go_to_cart()
    cart.should_contain()

    cart.checkout().should_be_loaded()

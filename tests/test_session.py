"""
Session and access-control tests: protected routes, logout, reset and persistence.
"""

import allure
import pytest
from playwright.sync_api import Page, expect

from data.messages import LoginErrors
from data.products import BACKPACK, BIKE_LIGHT
from pages import CartPage, InventoryPage, LoginPage

pytestmark = allure.feature("Session & security")

PROTECTED_PATHS = [
    "/inventory.html",
    "/cart.html",
    "/checkout-step-one.html",
    "/checkout-step-two.html",
    "/checkout-complete.html",
    "/inventory-item.html",
]


@pytest.mark.smoke
@pytest.mark.parametrize("path", PROTECTED_PATHS)
def test_protected_route_requires_login(page: Page, path: str):
    page.goto(path)

    login = LoginPage(page).should_be_loaded()
    login.should_show_error(LoginErrors.not_logged_in(path))


@pytest.mark.smoke
def test_logout_returns_to_login_and_clears_session(inventory_page: InventoryPage):
    login = inventory_page.header.logout()

    assert not [c for c in login.page.context.cookies() if c["name"] == "session-username"]


def test_back_button_after_logout_does_not_restore_session(inventory_page: InventoryPage):
    login = inventory_page.header.logout()

    login.page.go_back()

    LoginPage(login.page).should_be_loaded().should_show_error(LoginErrors.not_logged_in("/inventory.html"))


def test_session_survives_page_reload(inventory_page: InventoryPage):
    inventory_page.page.reload()

    inventory_page.should_be_loaded()


@pytest.mark.regression
def test_cart_persists_after_reload(inventory_page: InventoryPage):
    inventory_page.add_products(BACKPACK, BIKE_LIGHT)

    inventory_page.page.reload()

    inventory_page.should_be_loaded().header.should_have_cart_count(2)
    expect(inventory_page.remove_button(BACKPACK)).to_be_visible()


@pytest.mark.regression
def test_reset_app_state_empties_cart(cart_page: CartPage):
    cart_page.header.reset_app_state()
    cart_page.page.reload()

    CartPage(cart_page.page).should_be_loaded().should_contain()
    cart_page.header.should_have_cart_count(0)


def test_all_items_link_returns_to_inventory(cart_page: CartPage):
    cart_page.header.go_to_all_items().should_be_loaded()

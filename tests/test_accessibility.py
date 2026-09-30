"""
Automated accessibility checks with axe-core.

The build fails on ``critical`` and ``serious`` violations; the full axe report
(including minor/moderate findings) is attached to Allure for every page.
"""

import json

import allure
import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

from data.products import BACKPACK
from pages import BasePage, CartPage, InventoryPage, LoginPage

pytestmark = [allure.feature("Accessibility"), pytest.mark.a11y]

BLOCKING_IMPACTS = {"critical", "serious"}


def assert_no_blocking_violations(page: Page) -> None:
    results = Axe().run(page)
    violations = results.response["violations"]
    allure.attach(json.dumps(violations, indent=2), name="axe-violations", attachment_type=allure.attachment_type.JSON)

    blocking = [
        f"[{v['impact']}] {v['id']}: {v['help']} ({len(v['nodes'])} node(s))"
        for v in violations
        if v["impact"] in BLOCKING_IMPACTS
    ]
    assert not blocking, "Blocking accessibility violations:\n" + "\n".join(blocking)


@pytest.mark.smoke
def test_login_page_accessibility(login_page: LoginPage):
    assert_no_blocking_violations(login_page.page)


@pytest.mark.parametrize(
    "open_page",
    [
        pytest.param(lambda inventory: inventory, id="inventory"),
        pytest.param(lambda inventory: inventory.open_product(BACKPACK), id="product-detail"),
        pytest.param(lambda inventory: inventory.add_to_cart(BACKPACK).go_to_cart(), id="cart"),
        pytest.param(lambda inventory: inventory.add_to_cart(BACKPACK).go_to_cart().checkout(), id="checkout-info"),
    ],
)
def test_authenticated_pages_accessibility(inventory_page: InventoryPage, open_page):
    target: BasePage = open_page(inventory_page)

    assert_no_blocking_violations(target.page)


def test_empty_cart_accessibility(inventory_page: InventoryPage):
    cart: CartPage = inventory_page.go_to_cart()

    assert_no_blocking_violations(cart.page)

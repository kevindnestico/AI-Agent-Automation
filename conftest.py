"""
Shared pytest fixtures for the Saucedemo suite.

Fixture chain (each builds on the previous one):

    auth_state (session) ─┐
    user ─────────────────┴─> logged_in_page -> inventory_page
                                           └──> cart_page -> checkout_info_page -> checkout_overview_page

Authentication is performed through the UI only once per user and worker; the
resulting cookies are saved with ``storage_state`` and injected into every new
browser context, so tests start already logged in.
"""

import json
import time
from collections.abc import Callable
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Browser, Page, Playwright, expect

from config import settings
from data.customers import DEFAULT_CUSTOMER
from data.products import BACKPACK, BIKE_LIGHT, Product
from data.users import User
from pages import BasePage, CartPage, CheckoutInfoPage, CheckoutOverviewPage, InventoryPage, LoginPage


# --------------------------------------------------------------------------- #
# Playwright configuration
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session", autouse=True)
def _configure_playwright(playwright: Playwright) -> None:
    """Use Saucedemo's ``data-test`` attribute for ``get_by_test_id`` and set the expect timeout."""
    playwright.selectors.set_test_id_attribute("data-test")
    expect.set_options(timeout=settings.expect_timeout_ms)


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    """``--base-url`` / ``PYTEST_BASE_URL``, falling back to pytest.ini.

    pytest-base-url only applies the ini value on the xdist controller, so
    workers would otherwise get ``None``.
    """
    return pytestconfig.getoption("base_url") or pytestconfig.getini("base_url")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Extend pytest-playwright's defaults (base_url, video dir) with a fixed viewport."""
    return {**browser_context_args, "viewport": {"width": 1280, "height": 800}}


# --------------------------------------------------------------------------- #
# Authentication
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def auth_state(
    browser: Browser, browser_context_args: dict, tmp_path_factory: pytest.TempPathFactory
) -> Callable[[User], Path]:
    """Factory returning a ``storage_state`` file for a logged-in user.

    Logs in through the UI once per user (per xdist worker) and caches the file.
    The cache is refreshed before Saucedemo's 10-minute session cookie expires.
    """
    state_dir = tmp_path_factory.mktemp("auth")
    login_context_args = {k: v for k, v in browser_context_args.items() if k != "record_video_dir"}
    cache: dict[User, tuple[Path, float]] = {}

    def _get_state(user: User) -> Path:
        cached = cache.get(user)
        if cached and time.monotonic() - cached[1] < settings.auth_state_ttl_seconds:
            return cached[0]

        context = browser.new_context(**login_context_args)
        try:
            LoginPage(context.new_page()).open().login_as(user)
            path = state_dir / f"{user}.json"
            context.storage_state(path=path)
        finally:
            context.close()

        cache[user] = (path, time.monotonic())
        return path

    return _get_state


@pytest.fixture
def user(request: pytest.FixtureRequest) -> User:
    """User for ``logged_in_page``.

    Defaults to ``standard_user``. Override per test with
    ``@pytest.mark.user(User.PROBLEM)`` or with
    ``@pytest.mark.parametrize("user", [...], indirect=True)``.
    """
    if hasattr(request, "param"):
        return User(request.param)
    marker = request.node.get_closest_marker("user")
    return User(marker.args[0]) if marker else User.STANDARD


@pytest.fixture
def logged_in_page(new_context: Callable, auth_state: Callable[[User], Path], user: User) -> Page:
    """A page in a fresh context that is already authenticated as ``user``.

    Uses pytest-playwright's ``new_context`` so tracing/video/screenshots
    configured on the CLI are also recorded for this context.
    """
    context = new_context(storage_state=auth_state(user))
    page = context.new_page()
    with allure.step(f"Start session as '{user}' (storage_state)"):
        InventoryPage(page).open()
    return page


# --------------------------------------------------------------------------- #
# Page-level fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Unauthenticated login page."""
    return LoginPage(page).open()


@pytest.fixture
def inventory_page(logged_in_page: Page) -> InventoryPage:
    return InventoryPage(logged_in_page)


@pytest.fixture
def cart_products() -> tuple[Product, ...]:
    """Products pre-loaded by ``cart_page``. Override with ``@pytest.mark.parametrize("cart_products", ...)``."""
    return (BACKPACK, BIKE_LIGHT)


def seed_cart(page: Page, products: tuple[Product, ...]) -> None:
    """Put products in the cart through localStorage, skipping the UI.

    Test preconditions don't need to exercise the add-to-cart flow (that has
    its own tests), so this makes cart/checkout tests faster and less brittle.
    """
    ids = json.dumps([product.id for product in products])
    page.evaluate("ids => localStorage.setItem('cart-contents', ids)", ids)


@pytest.fixture
def cart_page(inventory_page: InventoryPage, cart_products: tuple[Product, ...]) -> CartPage:
    """Cart page with ``cart_products`` already in it."""
    with allure.step(f"Seed cart with {[p.name for p in cart_products]}"):
        seed_cart(inventory_page.page, cart_products)
    return CartPage(inventory_page.page).open()


@pytest.fixture
def checkout_info_page(cart_page: CartPage) -> CheckoutInfoPage:
    return cart_page.checkout()


@pytest.fixture
def checkout_overview_page(checkout_info_page: CheckoutInfoPage) -> CheckoutOverviewPage:
    return checkout_info_page.fill_customer(DEFAULT_CUSTOMER).continue_to_overview()


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def _find_page(item: pytest.Item) -> Page | None:
    """Return the Playwright page used by a test, if any."""
    for value in getattr(item, "funcargs", {}).values():
        if isinstance(value, Page):
            return value
        if isinstance(value, BasePage):
            return value.page
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Attach a screenshot and the current URL to Allure when a test fails.

    Runs during the ``call`` phase, before fixtures are torn down, so the page
    is still open in the state that caused the failure.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    page = _find_page(item)
    if page is None or page.is_closed():
        return
    try:
        allure.attach(
            page.screenshot(full_page=True),
            name="screenshot-on-failure",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(page.url, name="url-on-failure", attachment_type=allure.attachment_type.URI_LIST)
    except Exception as error:  # reporting must never mask the real failure
        allure.attach(str(error), name="attachment-error", attachment_type=allure.attachment_type.TEXT)

"""
Network-level checks: console/HTTP errors, resilience and hosting behavior.
"""

import re
from urllib.parse import urlparse

import allure
import pytest
from playwright.sync_api import Page, Response, Route

from data.customers import DEFAULT_CUSTOMER
from data.products import BACKPACK
from data.users import User
from pages import InventoryPage, LoginPage

pytestmark = allure.feature("Network")


def complete_purchase_through_ui(page: Page) -> None:
    """Full purchase using only clicks (no direct navigation)."""
    inventory = LoginPage(page).open().login_as(User.STANDARD)
    cart = inventory.add_to_cart(BACKPACK).go_to_cart()
    cart.checkout().fill_customer(DEFAULT_CUSTOMER).continue_to_overview().finish().back_home()


@pytest.mark.regression
def test_no_console_or_http_errors_during_purchase(page: Page, base_url: str):
    """The shop itself must not produce errors during a purchase.

    Third-party calls (e.g. Saucedemo's telemetry to events.backtrace.io, which
    answers 401 on CI runners) are outside the app under test: they are
    reported in Allure for visibility but do not fail the test.
    """
    app_host = urlparse(base_url).hostname
    problems: list[str] = []
    third_party: list[str] = []

    def record(url: str | None, message: str) -> None:
        is_first_party = not url or urlparse(url).hostname == app_host
        (problems if is_first_party else third_party).append(message)

    page.on(
        "console",
        lambda msg: record(msg.location.get("url"), f"console.{msg.type}: {msg.text}") if msg.type == "error" else None,
    )
    page.on("pageerror", lambda error: problems.append(f"uncaught: {error}"))
    page.on("requestfailed", lambda request: record(request.url, f"failed: {request.url}"))
    page.on(
        "response",
        lambda response: (
            record(response.url, f"HTTP {response.status}: {response.url}") if response.status >= 400 else None
        ),
    )

    complete_purchase_through_ui(page)

    if third_party:
        allure.attach("\n".join(third_party), name="third-party-errors", attachment_type=allure.attachment_type.TEXT)
    assert not problems, "Errors during purchase flow:\n" + "\n".join(problems)


@pytest.mark.regression
def test_purchase_works_with_images_blocked(page: Page):
    """The shop must stay usable when images fail to load (slow CDN, data saver)."""
    blocked: list[str] = []

    def block_images(route: Route) -> None:
        blocked.append(route.request.url)
        route.abort()

    page.route(re.compile(r"\.(png|jpe?g|svg|gif|webp)(\?.*)?$"), block_images)

    complete_purchase_through_ui(page)

    assert blocked, "Expected at least one image request to be intercepted"


@pytest.mark.regression
def test_static_assets_served_with_cache_headers(page: Page):
    responses: list[Response] = []
    page.on("response", lambda response: responses.append(response))

    LoginPage(page).open()

    assets = [r for r in responses if re.search(r"\.(js|css)$", r.url)]
    assert assets, "Expected JS/CSS bundles to be loaded"
    for response in assets:
        assert response.ok, f"{response.url} returned {response.status}"
        assert response.headers.get("cache-control"), f"{response.url} has no Cache-Control header"


@pytest.mark.known_bug
@pytest.mark.xfail(
    reason="Known bug: deep links are served with HTTP 404 by the static host; the SPA renders via fallback",
    raises=AssertionError,
)
def test_deep_link_returns_http_200(inventory_page: InventoryPage):
    response = inventory_page.page.goto(InventoryPage.PATH)

    assert response is not None
    assert response.status == 200, f"GET {InventoryPage.PATH} returned HTTP {response.status}"

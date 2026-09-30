"""
Cross-user visual regression.

Instead of storing OS/browser-specific baselines in the repo, the reference
image is captured in the same run from ``standard_user`` and compared with the
same page rendered for each other user. The comparison is therefore
deterministic on any machine and in any browser.
"""

from collections.abc import Callable

import allure
import pytest

from config import settings
from data import known_bugs
from data.users import LOGIN_CAPABLE_USERS, User
from pages import InventoryPage
from utils.visual import attach_comparison, compare_screenshots

pytestmark = [allure.feature("Visual regression"), pytest.mark.visual]


@pytest.fixture
def inventory_screenshot(new_context: Callable, auth_state: Callable) -> Callable[[User], bytes]:
    def _capture(user: User) -> bytes:
        page = new_context(storage_state=auth_state(user)).new_page()
        InventoryPage(page).open()
        page.wait_for_load_state("networkidle")
        page.wait_for_function("[...document.images].every(img => img.complete)")
        return page.screenshot(full_page=True, animations="disabled")

    return _capture


@pytest.mark.parametrize(
    "user",
    known_bugs.users_with_known_bugs(
        known_bugs.VISUAL_DIFFERENCES,
        users=[user for user in LOGIN_CAPABLE_USERS if user is not User.STANDARD],
    ),
)
def test_inventory_looks_like_standard_user(inventory_screenshot: Callable[[User], bytes], user: User):
    expected = inventory_screenshot(User.STANDARD)
    actual = inventory_screenshot(user)

    diff = compare_screenshots(expected, actual)
    attach_comparison(expected, actual, diff)

    assert diff.diff_ratio <= settings.visual_diff_tolerance, (
        f"{diff.diff_ratio:.2%} of pixels differ from standard_user (tolerance {settings.visual_diff_tolerance:.2%})"
    )

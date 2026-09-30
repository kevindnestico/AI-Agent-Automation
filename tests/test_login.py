"""
Login functionality tests for Saucedemo.
"""

import json
import time
from pathlib import Path

import allure
import pytest

from config import settings
from data import known_bugs
from data.messages import LoginErrors
from data.users import LOGIN_CAPABLE_USERS, User
from pages import LoginPage

pytestmark = allure.feature("Login")

LOGIN_CASES = json.loads((Path(__file__).parents[1] / "data" / "login_cases.json").read_text())


@pytest.mark.smoke
def test_login_successful_standard_user(login_page: LoginPage):
    inventory = login_page.login_as(User.STANDARD)

    assert inventory.get_product_names(), "Inventory should list products after login"


@pytest.mark.smoke
@pytest.mark.parametrize("case", LOGIN_CASES, ids=[case["id"] for case in LOGIN_CASES])
def test_login_rejected(login_page: LoginPage, case: dict):
    """Data-driven negative login scenarios loaded from data/login_cases.json."""
    login_page.login(case["username"], case["password"])

    login_page.should_show_error(getattr(LoginErrors, case["error"]))
    login_page.should_be_loaded()


@pytest.mark.parametrize("user", LOGIN_CAPABLE_USERS, ids=str)
def test_login_successful_all_valid_users(login_page: LoginPage, user: User):
    login_page.login_as(user)


@pytest.mark.regression
@pytest.mark.parametrize("user", known_bugs.users_with_known_bugs(known_bugs.SLOW_LOGIN))
def test_login_response_time_within_sla(login_page: LoginPage, user: User):
    start = time.perf_counter()
    login_page.login_as(user)
    elapsed = time.perf_counter() - start

    allure.dynamic.parameter("elapsed_seconds", round(elapsed, 2))
    assert elapsed < settings.login_sla_seconds, f"Login took {elapsed:.2f}s (SLA {settings.login_sla_seconds}s)"


def test_login_error_can_be_dismissed(login_page: LoginPage):
    login_page.login("", "")
    login_page.should_show_error(LoginErrors.USERNAME_REQUIRED)

    login_page.page.get_by_test_id("error-button").click()

    login_page.error_message.wait_for(state="hidden")

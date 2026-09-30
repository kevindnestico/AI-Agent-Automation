"""
Login functionality tests for Saucedemo.
"""

import allure
import pytest

from config import settings
from data.messages import LoginErrors
from data.users import User
from pages import InventoryPage, LoginPage

pytestmark = allure.feature("Login")


@pytest.mark.smoke
def test_login_successful_standard_user(login_page: LoginPage):
    inventory = login_page.login_as(User.STANDARD)

    inventory.should_be_loaded()
    assert inventory.get_product_names(), "Inventory should list products after login"


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("username", "password", "expected_error"),
    [
        pytest.param("invalid_user", settings.password, LoginErrors.INVALID_CREDENTIALS, id="invalid-username"),
        pytest.param(User.STANDARD, "wrong_password", LoginErrors.INVALID_CREDENTIALS, id="invalid-password"),
        pytest.param("", settings.password, LoginErrors.USERNAME_REQUIRED, id="empty-username"),
        pytest.param(User.STANDARD, "", LoginErrors.PASSWORD_REQUIRED, id="empty-password"),
        pytest.param("", "", LoginErrors.USERNAME_REQUIRED, id="both-empty"),
        pytest.param(User.LOCKED_OUT, settings.password, LoginErrors.LOCKED_OUT, id="locked-out-user"),
    ],
)
def test_login_rejected(login_page: LoginPage, username: str, password: str, expected_error: str):
    login_page.login(username, password)

    login_page.should_show_error(expected_error)
    login_page.should_be_loaded()


@pytest.mark.parametrize("user", [User.PROBLEM, User.PERFORMANCE_GLITCH, User.ERROR, User.VISUAL])
def test_login_successful_special_users(login_page: LoginPage, user: User):
    login_page.login_as(user)

    InventoryPage(login_page.page).should_be_loaded()

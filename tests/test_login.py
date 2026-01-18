"""
Login functionality tests for Saucedemo.
"""
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_login_successful_standard_user(page: Page):
    """
    Test successful login with standard_user credentials.
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.verify_login_page_loaded()
    
    # Perform login
    login_page.login("standard_user", "secret_sauce")
    
    # Verify successful login by checking inventory page loads
    inventory_page = InventoryPage(page)
    inventory_page.verify_inventory_page_loaded()
    
    # Verify URL changed to inventory
    assert "inventory.html" in page.url, "Should redirect to inventory page after login"


@pytest.mark.smoke
def test_login_invalid_username(page: Page):
    """
    Test login with invalid username.
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("invalid_user", "secret_sauce")
    
    # Verify error message is displayed
    assert login_page.is_error_displayed(), "Error message should be displayed"
    
    error_message = login_page.get_error_message()
    assert "Epic sadface" in error_message, "Error should contain 'Epic sadface'"
    assert "do not match" in error_message, "Error should mention credentials don't match"
    
    # Verify still on login page
    assert page.url == "https://www.saucedemo.com/", "Should remain on login page"


@pytest.mark.smoke
def test_login_invalid_password(page: Page):
    """
    Test login with invalid password.
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "wrong_password")
    
    # Verify error message
    assert login_page.is_error_displayed(), "Error message should be displayed"
    
    error_message = login_page.get_error_message()
    assert "Epic sadface" in error_message, "Error should contain 'Epic sadface'"
    assert "do not match" in error_message, "Error should mention credentials don't match"


def test_login_empty_username(page: Page):
    """
    Test login with empty username field.
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("", "secret_sauce")
    
    # Verify error message
    assert login_page.is_error_displayed(), "Error message should be displayed"
    
    error_message = login_page.get_error_message()
    assert "Epic sadface" in error_message, "Error should contain 'Epic sadface'"
    assert "Username is required" in error_message, "Error should mention username required"


def test_login_empty_password(page: Page):
    """
    Test login with empty password field.
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "")
    
    # Verify error message
    assert login_page.is_error_displayed(), "Error message should be displayed"
    
    error_message = login_page.get_error_message()
    assert "Epic sadface" in error_message, "Error should contain 'Epic sadface'"
    assert "Password is required" in error_message, "Error should mention password required"


def test_login_locked_out_user(page: Page):
    """
    Test login with locked out user.
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("locked_out_user", "secret_sauce")
    
    # Verify error message for locked user
    assert login_page.is_error_displayed(), "Error message should be displayed"
    
    error_message = login_page.get_error_message()
    assert "Epic sadface" in error_message, "Error should contain 'Epic sadface'"
    assert "locked out" in error_message.lower(), "Error should mention user is locked out"
    
    # Verify still on login page
    assert page.url == "https://www.saucedemo.com/", "Should remain on login page"


def test_login_problem_user(page: Page):
    """
    Test login with problem_user (should succeed but has issues).
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("problem_user", "secret_sauce")
    
    # Problem user can login but images are broken
    inventory_page = InventoryPage(page)
    inventory_page.verify_inventory_page_loaded()
    
    assert "inventory.html" in page.url, "Should redirect to inventory page"


def test_login_performance_glitch_user(page: Page):
    """
    Test login with performance_glitch_user (slow loading).
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("performance_glitch_user", "secret_sauce")
    
    # Should succeed but may be slow
    inventory_page = InventoryPage(page)
    inventory_page.verify_inventory_page_loaded()
    
    assert "inventory.html" in page.url, "Should redirect to inventory page"


@pytest.mark.regression
def test_login_both_fields_empty(page: Page):
    """
    Test login with both username and password empty.
    
    Args:
        page: Playwright page instance from fixture
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("", "")
    
    # Verify error message
    assert login_page.is_error_displayed(), "Error message should be displayed"
    
    error_message = login_page.get_error_message()
    assert "Epic sadface" in error_message, "Error should contain 'Epic sadface'"
    assert "Username is required" in error_message, "Should prioritize username error"

"""
Negative test cases for checkout flow in Saucedemo.
"""
import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_info_page import CheckoutInfoPage
from pages.checkout_overview_page import CheckoutOverviewPage


@pytest.fixture
def checkout_info_page(page: Page) -> CheckoutInfoPage:
    """
    Fixture that navigates to checkout info page with items in cart.
    
    Args:
        page: Playwright page instance
        
    Returns:
        CheckoutInfoPage: Checkout info page instance
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add items and go to cart
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    
    # Proceed to checkout
    cart_page = CartPage(page)
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.verify_checkout_info_page_loaded()
    
    return checkout_info


@pytest.mark.smoke
def test_checkout_empty_first_name(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with empty first name field.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Fill with empty first name
    checkout_info.fill_info("", "Perez", "28001")
    checkout_info._continue_button.click()
    
    # Verify error is displayed
    assert checkout_info.is_error_displayed(), "Error should be displayed"
    
    error_message = checkout_info.get_error_message()
    assert "Error" in error_message or "First Name is required" in error_message, \
        "Should show first name required error"


@pytest.mark.smoke
def test_checkout_empty_last_name(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with empty last name field.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Fill with empty last name
    checkout_info.fill_info("Juan", "", "28001")
    checkout_info._continue_button.click()
    
    # Verify error is displayed
    assert checkout_info.is_error_displayed(), "Error should be displayed"
    
    error_message = checkout_info.get_error_message()
    assert "Error" in error_message or "Last Name is required" in error_message, \
        "Should show last name required error"


@pytest.mark.smoke
def test_checkout_empty_postal_code(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with empty postal code field.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Fill with empty postal code
    checkout_info.fill_info("Juan", "Perez", "")
    checkout_info._continue_button.click()
    
    # Verify error is displayed
    assert checkout_info.is_error_displayed(), "Error should be displayed"
    
    error_message = checkout_info.get_error_message()
    assert "Error" in error_message or "Postal Code is required" in error_message, \
        "Should show postal code required error"


def test_checkout_all_fields_empty(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with all fields empty.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Leave all fields empty and try to continue
    checkout_info.fill_info("", "", "")
    checkout_info._continue_button.click()
    
    # Verify error is displayed
    assert checkout_info.is_error_displayed(), "Error should be displayed"
    
    error_message = checkout_info.get_error_message()
    assert "Error" in error_message or "required" in error_message, \
        "Should show field required error"


def test_checkout_cancel_from_info_page(checkout_info_page: CheckoutInfoPage):
    """
    Test canceling checkout from info page returns to cart.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Cancel checkout
    checkout_info.cancel_checkout()
    
    # Verify back on cart page
    assert "cart.html" in checkout_info.get_current_url(), \
        "Should return to cart page after cancel"


def test_checkout_cancel_from_overview_page(page: Page):
    """
    Test canceling checkout from overview page returns to inventory.
    
    Args:
        page: Playwright page instance
    """
    # Login and add items
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    
    # Proceed to checkout and fill info
    cart_page = CartPage(page)
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("Juan", "Perez", "28001")
    checkout_info.continue_to_overview()
    
    # Cancel from overview
    checkout_overview = CheckoutOverviewPage(page)
    checkout_overview.verify_checkout_overview_page_loaded()
    checkout_overview.cancel_checkout()
    
    # Verify back on inventory page
    assert "inventory.html" in page.url, \
        "Should return to inventory page after cancel from overview"


@pytest.mark.regression
def test_checkout_special_characters_in_name(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with special characters in name fields.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Fill with special characters
    checkout_info.fill_info("J@hn!", "P#rez$", "28001")
    checkout_info.continue_to_overview()
    
    # Should succeed (Saucedemo accepts special characters)
    overview = CheckoutOverviewPage(checkout_info.page)
    overview.verify_checkout_overview_page_loaded()


@pytest.mark.regression
def test_checkout_very_long_names(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with very long name inputs.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Fill with very long strings
    long_name = "A" * 100
    checkout_info.fill_info(long_name, long_name, "28001")
    checkout_info.continue_to_overview()
    
    # Should succeed
    overview = CheckoutOverviewPage(checkout_info.page)
    overview.verify_checkout_overview_page_loaded()


@pytest.mark.regression
def test_checkout_numeric_names(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with numeric values in name fields.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Fill with numbers
    checkout_info.fill_info("12345", "67890", "28001")
    checkout_info.continue_to_overview()
    
    # Should succeed (Saucedemo accepts numeric names)
    overview = CheckoutOverviewPage(checkout_info.page)
    overview.verify_checkout_overview_page_loaded()


def test_checkout_from_empty_cart(page: Page):
    """
    Test attempting to checkout with empty cart (if possible).
    
    Args:
        page: Playwright page instance
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Go to cart without adding items
    inventory_page = InventoryPage(page)
    inventory_page.go_to_cart()
    
    cart_page = CartPage(page)
    
    # Try to checkout with empty cart
    # Note: The checkout button should still be visible but cart should be empty
    if cart_page.is_cart_empty():
        cart_page.proceed_to_checkout()
        
        # Should still navigate to checkout (Saucedemo allows this)
        assert "checkout-step-one.html" in page.url, \
            "Should allow checkout even with empty cart"


@pytest.mark.regression
def test_checkout_invalid_postal_code_format(checkout_info_page: CheckoutInfoPage):
    """
    Test checkout with invalid postal code format.
    
    Args:
        checkout_info_page: Checkout info page fixture
    """
    checkout_info = checkout_info_page
    
    # Fill with letters in postal code (usually numeric)
    checkout_info.fill_info("Juan", "Perez", "ABCDE")
    checkout_info.continue_to_overview()
    
    # Saucedemo accepts any postal code format
    overview = CheckoutOverviewPage(checkout_info.page)
    overview.verify_checkout_overview_page_loaded()

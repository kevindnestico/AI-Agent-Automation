"""
Happy path test for complete checkout flow in Saucedemo.
"""
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_info_page import CheckoutInfoPage
from pages.checkout_overview_page import CheckoutOverviewPage
from pages.checkout_complete_page import CheckoutCompletePage


@pytest.mark.smoke
def test_checkout_happy_path(page: Page):
    """
    Test complete checkout happy path flow.
    
    Scenario:
        1. Login with standard_user
        2. Add Sauce Labs Backpack and Bike Light to cart
        3. Navigate to cart and verify 2 items
        4. Proceed to checkout and fill information
        5. Complete purchase
        6. Verify success message
    
    Args:
        page: Playwright page instance from fixture
    """
    # Step 1: Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.verify_login_page_loaded()
    login_page.login("standard_user", "secret_sauce")
    
    # Step 2: Add products to cart
    inventory_page = InventoryPage(page)
    inventory_page.verify_inventory_page_loaded()
    
    # Add Sauce Labs Backpack
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    
    # Add Sauce Labs Bike Light
    inventory_page.add_to_cart_by_name("Sauce Labs Bike Light")
    
    # Verify cart badge shows 2 items
    assert inventory_page.get_cart_count() == 2, "Cart should contain 2 items"
    
    # Step 3: Go to cart and verify items
    inventory_page.go_to_cart()
    
    cart_page = CartPage(page)
    cart_page.verify_cart_page_loaded()
    
    # Strong assertions for cart content
    cart_item_count = cart_page.get_cart_item_count()
    assert cart_item_count == 2, f"Expected 2 items in cart, but found {cart_item_count}"
    
    cart_item_names = cart_page.get_cart_item_names()
    assert "Sauce Labs Backpack" in cart_item_names, "Backpack should be in cart"
    assert "Sauce Labs Bike Light" in cart_item_names, "Bike Light should be in cart"
    
    # Verify cart is not empty
    assert not cart_page.is_cart_empty(), "Cart should not be empty"
    
    # Step 4: Proceed to checkout and fill information
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.verify_checkout_info_page_loaded()
    
    # Fill checkout information: Juan Perez, postal code 28001
    checkout_info.fill_info(
        first_name="Juan",
        last_name="Perez",
        postal_code="28001"
    )
    
    checkout_info.continue_to_overview()
    
    # Step 5: Verify overview and finish purchase
    checkout_overview = CheckoutOverviewPage(page)
    checkout_overview.verify_checkout_overview_page_loaded()
    
    # Verify items in overview
    overview_item_count = checkout_overview.get_item_count()
    assert overview_item_count == 2, f"Expected 2 items in overview, but found {overview_item_count}"
    
    overview_item_names = checkout_overview.get_item_names()
    assert "Sauce Labs Backpack" in overview_item_names, "Backpack should be in checkout overview"
    assert "Sauce Labs Bike Light" in overview_item_names, "Bike Light should be in checkout overview"
    
    # Verify payment summary is visible
    checkout_overview.verify_payment_summary_visible()
    
    # Get payment summary and verify amounts are positive
    payment_summary = checkout_overview.get_payment_summary()
    assert payment_summary["subtotal"] > 0, "Subtotal should be greater than 0"
    assert payment_summary["tax"] > 0, "Tax should be greater than 0"
    assert payment_summary["total"] > 0, "Total should be greater than 0"
    
    # Verify total = subtotal + tax
    expected_total = round(payment_summary["subtotal"] + payment_summary["tax"], 2)
    actual_total = payment_summary["total"]
    assert actual_total == expected_total, f"Total {actual_total} should equal subtotal + tax {expected_total}"
    
    # Finish the purchase
    checkout_overview.finish()
    
    # Step 6: Verify order completion
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_checkout_complete_page_loaded()
    checkout_complete.verify_order_complete()
    
    # Strong assertion for success message
    thank_you_message = checkout_complete.get_thank_you_message()
    expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")
    assert thank_you_message == "Thank you for your order!", f"Expected 'Thank you for your order!' but got '{thank_you_message}'"
    
    # Verify success image is displayed
    assert checkout_complete.is_success_image_visible(), "Success image should be visible"
    
    # Verify completion text is present
    complete_text = checkout_complete.get_complete_text()
    assert len(complete_text) > 0, "Completion text should not be empty"
    assert "dispatched" in complete_text.lower(), "Completion text should mention dispatch"
    
    # Optional: Return to home page
    checkout_complete.go_back_home()
    inventory_page.verify_inventory_page_loaded()

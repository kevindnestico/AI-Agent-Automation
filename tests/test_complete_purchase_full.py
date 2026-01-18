"""
End-to-end complete purchase tests with variations for Saucedemo.
"""
import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_info_page import CheckoutInfoPage
from pages.checkout_overview_page import CheckoutOverviewPage
from pages.checkout_complete_page import CheckoutCompletePage


@pytest.mark.smoke
@pytest.mark.regression
def test_complete_purchase_single_item(page: Page):
    """
    Test complete purchase flow with a single item.
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add single item
    inventory_page = InventoryPage(page)
    inventory_page.verify_inventory_page_loaded()
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    
    # Verify cart badge
    assert inventory_page.get_cart_count() == 1
    
    # Go to cart
    inventory_page.go_to_cart()
    cart_page = CartPage(page)
    cart_page.verify_cart_page_loaded()
    
    # Proceed to checkout
    cart_page.proceed_to_checkout()
    
    # Fill checkout info
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("John", "Doe", "12345")
    checkout_info.continue_to_overview()
    
    # Verify and finish
    checkout_overview = CheckoutOverviewPage(page)
    checkout_overview.verify_checkout_overview_page_loaded()
    checkout_overview.finish()
    
    # Verify completion
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_order_complete()
    assert checkout_complete.get_thank_you_message() == "Thank you for your order!"


@pytest.mark.regression
def test_complete_purchase_multiple_items(page: Page):
    """
    Test complete purchase flow with multiple items.
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add multiple items
    inventory_page = InventoryPage(page)
    items_to_buy = [
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Bolt T-Shirt",
        "Sauce Labs Fleece Jacket"
    ]
    
    for item in items_to_buy:
        inventory_page.add_to_cart_by_name(item)
    
    assert inventory_page.get_cart_count() == len(items_to_buy)
    
    # Proceed through checkout
    inventory_page.go_to_cart()
    
    cart_page = CartPage(page)
    assert cart_page.get_cart_item_count() == len(items_to_buy)
    cart_page.proceed_to_checkout()
    
    # Fill info
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("Maria", "Garcia", "90210")
    checkout_info.continue_to_overview()
    
    # Verify overview
    checkout_overview = CheckoutOverviewPage(page)
    assert checkout_overview.get_item_count() == len(items_to_buy)
    
    payment_summary = checkout_overview.get_payment_summary()
    assert payment_summary["total"] > 0
    
    # Complete purchase
    checkout_overview.finish()
    
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_order_complete()


@pytest.mark.regression
def test_complete_purchase_all_items(page: Page):
    """
    Test complete purchase flow with all available items.
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add all items
    inventory_page = InventoryPage(page)
    all_products = inventory_page.get_product_names()
    
    for product in all_products:
        inventory_page.add_to_cart_by_name(product)
    
    # Verify all items added
    assert inventory_page.get_cart_count() == len(all_products)
    
    # Complete checkout
    inventory_page.go_to_cart()
    cart_page = CartPage(page)
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("Test", "User", "12345")
    checkout_info.continue_to_overview()
    
    checkout_overview = CheckoutOverviewPage(page)
    checkout_overview.finish()
    
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_order_complete()


def test_complete_purchase_with_item_removal(page: Page):
    """
    Test purchase flow where user adds items then removes some before checkout.
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add three items
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.add_to_cart_by_name("Sauce Labs Bike Light")
    inventory_page.add_to_cart_by_name("Sauce Labs Bolt T-Shirt")
    
    # Go to cart and remove one item
    inventory_page.go_to_cart()
    cart_page = CartPage(page)
    cart_page.remove_item("Sauce Labs Bolt T-Shirt")
    
    # Verify only 2 items remain
    assert cart_page.get_cart_item_count() == 2
    
    # Complete checkout with remaining items
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("Carlos", "Martinez", "55555")
    checkout_info.continue_to_overview()
    
    checkout_overview = CheckoutOverviewPage(page)
    assert checkout_overview.get_item_count() == 2
    checkout_overview.finish()
    
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_order_complete()


def test_complete_purchase_different_user_variations(page: Page):
    """
    Test purchase with different customer information variations.
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add item
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Onesie")
    inventory_page.go_to_cart()
    
    # Checkout with different info
    cart_page = CartPage(page)
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    # Use international characters
    checkout_info.fill_info("José", "Rodríguez", "28001")
    checkout_info.continue_to_overview()
    
    checkout_overview = CheckoutOverviewPage(page)
    checkout_overview.finish()
    
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_order_complete()


@pytest.mark.regression
def test_complete_purchase_verify_payment_calculation(page: Page):
    """
    Test purchase flow with payment calculation verification.
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add items with known prices
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.add_to_cart_by_name("Sauce Labs Bike Light")
    
    # Get prices from inventory
    inventory_page.go_to_cart()
    
    cart_page = CartPage(page)
    cart_prices = cart_page.get_cart_item_prices()
    expected_subtotal = sum(cart_prices)
    
    # Proceed to overview
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("Finance", "Tester", "12345")
    checkout_info.continue_to_overview()
    
    # Verify payment summary
    checkout_overview = CheckoutOverviewPage(page)
    payment_summary = checkout_overview.get_payment_summary()
    
    # Verify subtotal matches
    assert payment_summary["subtotal"] == expected_subtotal, \
        f"Subtotal {payment_summary['subtotal']} should match expected {expected_subtotal}"
    
    # Verify tax is calculated
    assert payment_summary["tax"] > 0, "Tax should be greater than 0"
    
    # Verify total = subtotal + tax
    calculated_total = round(payment_summary["subtotal"] + payment_summary["tax"], 2)
    assert payment_summary["total"] == calculated_total, \
        "Total should equal subtotal plus tax"
    
    # Complete purchase
    checkout_overview.finish()
    
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_order_complete()


def test_complete_purchase_return_to_inventory_after_completion(page: Page):
    """
    Test returning to inventory after completing purchase.
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Complete a quick purchase
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    
    cart_page = CartPage(page)
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("Test", "Return", "12345")
    checkout_info.continue_to_overview()
    
    checkout_overview = CheckoutOverviewPage(page)
    checkout_overview.finish()
    
    # Return home
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.go_back_home()
    
    # Verify back on inventory and cart is empty
    inventory_page.verify_inventory_page_loaded()
    assert inventory_page.get_cart_count() == 0, \
        "Cart should be empty after completing purchase"


@pytest.mark.slow
def test_complete_purchase_sorted_items(page: Page):
    """
    Test purchase flow with sorted items (price low to high).
    
    Args:
        page: Playwright page instance from fixture
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Sort items by price
    inventory_page = InventoryPage(page)
    inventory_page.sort_products("Price (low to high)")
    
    # Get sorted products and add cheapest ones
    product_names = inventory_page.get_product_names()
    inventory_page.add_to_cart_by_name(product_names[0])
    inventory_page.add_to_cart_by_name(product_names[1])
    
    # Complete purchase
    inventory_page.go_to_cart()
    
    cart_page = CartPage(page)
    cart_page.proceed_to_checkout()
    
    checkout_info = CheckoutInfoPage(page)
    checkout_info.fill_info("Budget", "Shopper", "00000")
    checkout_info.continue_to_overview()
    
    checkout_overview = CheckoutOverviewPage(page)
    checkout_overview.finish()
    
    checkout_complete = CheckoutCompletePage(page)
    checkout_complete.verify_order_complete()

"""
Shopping cart functionality tests for Saucedemo.
"""
import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


@pytest.fixture
def cart_with_items(page: Page) -> tuple[CartPage, InventoryPage]:
    """
    Fixture that provides a cart page with items already added.
    
    Args:
        page: Playwright page instance
        
    Returns:
        tuple: (CartPage, InventoryPage) instances
    """
    # Login
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    # Add items to cart
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.add_to_cart_by_name("Sauce Labs Bike Light")
    
    # Go to cart
    inventory_page.go_to_cart()
    
    cart_page = CartPage(page)
    cart_page.verify_cart_page_loaded()
    
    return cart_page, inventory_page


@pytest.mark.smoke
def test_cart_displays_added_items(cart_with_items: tuple[CartPage, InventoryPage]):
    """
    Test that cart displays all added items correctly.
    
    Args:
        cart_with_items: Fixture with cart page and items
    """
    cart_page, _ = cart_with_items
    
    # Verify item count
    assert cart_page.get_cart_item_count() == 2, "Cart should have 2 items"
    
    # Verify item names
    item_names = cart_page.get_cart_item_names()
    assert "Sauce Labs Backpack" in item_names, "Backpack should be in cart"
    assert "Sauce Labs Bike Light" in item_names, "Bike Light should be in cart"


@pytest.mark.smoke
def test_remove_item_from_cart(cart_with_items: tuple[CartPage, InventoryPage]):
    """
    Test removing an item from the cart.
    
    Args:
        cart_with_items: Fixture with cart page and items
    """
    cart_page, _ = cart_with_items
    
    # Remove one item
    cart_page.remove_item("Sauce Labs Backpack")
    
    # Verify count decreased
    assert cart_page.get_cart_item_count() == 1, "Cart should have 1 item after removal"
    
    # Verify correct item was removed
    item_names = cart_page.get_cart_item_names()
    assert "Sauce Labs Backpack" not in item_names, "Backpack should be removed"
    assert "Sauce Labs Bike Light" in item_names, "Bike Light should still be in cart"


def test_remove_all_items_from_cart(cart_with_items: tuple[CartPage, InventoryPage]):
    """
    Test removing all items from cart.
    
    Args:
        cart_with_items: Fixture with cart page and items
    """
    cart_page, _ = cart_with_items
    
    # Remove both items
    cart_page.remove_item("Sauce Labs Backpack")
    cart_page.remove_item("Sauce Labs Bike Light")
    
    # Verify cart is empty
    assert cart_page.is_cart_empty(), "Cart should be empty after removing all items"
    assert cart_page.get_cart_item_count() == 0, "Cart count should be 0"


@pytest.mark.smoke
def test_continue_shopping_from_cart(cart_with_items: tuple[CartPage, InventoryPage]):
    """
    Test continue shopping button returns to inventory.
    
    Args:
        cart_with_items: Fixture with cart page and items
    """
    cart_page, inventory_page = cart_with_items
    
    # Click continue shopping
    cart_page.continue_shopping()
    
    # Verify back on inventory page
    inventory_page.verify_inventory_page_loaded()
    assert "inventory.html" in cart_page.get_current_url(), \
        "Should return to inventory page"


@pytest.mark.smoke
def test_proceed_to_checkout_from_cart(cart_with_items: tuple[CartPage, InventoryPage]):
    """
    Test proceeding to checkout from cart.
    
    Args:
        cart_with_items: Fixture with cart page and items
    """
    cart_page, _ = cart_with_items
    
    # Proceed to checkout
    cart_page.proceed_to_checkout()
    
    # Verify URL changed to checkout
    assert "checkout-step-one.html" in cart_page.get_current_url(), \
        "Should navigate to checkout info page"


def test_cart_item_prices_displayed(cart_with_items: tuple[CartPage, InventoryPage]):
    """
    Test that item prices are displayed in cart.
    
    Args:
        cart_with_items: Fixture with cart page and items
    """
    cart_page, _ = cart_with_items
    
    # Get prices
    prices = cart_page.get_cart_item_prices()
    
    # Verify we have 2 prices
    assert len(prices) == 2, "Should have 2 item prices"
    
    # Verify all prices are positive
    for price in prices:
        assert price > 0, f"Price {price} should be greater than 0"


def test_empty_cart_navigation(page: Page):
    """
    Test navigating to cart when it's empty.
    
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
    
    # Verify cart page loads and is empty
    cart_page = CartPage(page)
    cart_page.verify_cart_page_loaded()
    assert cart_page.is_cart_empty(), "Cart should be empty"
    assert cart_page.get_cart_item_count() == 0, "Cart count should be 0"


@pytest.mark.regression
def test_cart_persists_items_after_navigation(page: Page):
    """
    Test that cart items persist after navigating away and back.
    
    Args:
        page: Playwright page instance
    """
    # Login and add items
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    inventory_page = InventoryPage(page)
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    
    # Go to cart
    inventory_page.go_to_cart()
    cart_page = CartPage(page)
    assert cart_page.get_cart_item_count() == 1, "Should have 1 item in cart"
    
    # Continue shopping
    cart_page.continue_shopping()
    
    # Go back to cart
    inventory_page.go_to_cart()
    
    # Verify item is still there
    assert cart_page.get_cart_item_count() == 1, "Item should persist in cart"
    assert "Sauce Labs Backpack" in cart_page.get_cart_item_names(), \
        "Backpack should still be in cart"


def test_cart_badge_updates_after_removal(cart_with_items: tuple[CartPage, InventoryPage]):
    """
    Test that cart badge updates after removing items.
    
    Args:
        cart_with_items: Fixture with cart page and items
    """
    cart_page, inventory_page = cart_with_items
    
    # Remove one item
    cart_page.remove_item("Sauce Labs Backpack")
    
    # Go back to inventory to check badge
    cart_page.continue_shopping()
    
    # Verify badge shows 1
    assert inventory_page.get_cart_count() == 1, \
        "Cart badge should show 1 item after removal"

"""
Inventory page functionality tests for Saucedemo.
"""
import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@pytest.fixture
def logged_in_inventory_page(page: Page) -> InventoryPage:
    """
    Fixture that provides an inventory page with user already logged in.
    
    Args:
        page: Playwright page instance
        
    Returns:
        InventoryPage: Inventory page with user logged in
    """
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")
    
    inventory_page = InventoryPage(page)
    inventory_page.verify_inventory_page_loaded()
    return inventory_page


@pytest.mark.smoke
def test_add_single_item_to_cart(logged_in_inventory_page: InventoryPage):
    """
    Test adding a single item to cart.
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Initially cart should be empty
    assert inventory_page.get_cart_count() == 0, "Cart should be empty initially"
    
    # Add item to cart
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    
    # Verify cart badge shows 1
    assert inventory_page.get_cart_count() == 1, "Cart should have 1 item"


@pytest.mark.smoke
def test_add_multiple_items_to_cart(logged_in_inventory_page: InventoryPage):
    """
    Test adding multiple items to cart.
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Add three items
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.add_to_cart_by_name("Sauce Labs Bike Light")
    inventory_page.add_to_cart_by_name("Sauce Labs Bolt T-Shirt")
    
    # Verify cart count
    assert inventory_page.get_cart_count() == 3, "Cart should have 3 items"


def test_remove_item_from_inventory(logged_in_inventory_page: InventoryPage):
    """
    Test removing an item from cart via inventory page.
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Add item
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    assert inventory_page.get_cart_count() == 1, "Cart should have 1 item"
    
    # Remove item
    inventory_page.remove_from_cart_by_name("Sauce Labs Backpack")
    
    # Verify cart is empty
    assert inventory_page.get_cart_count() == 0, "Cart should be empty after removal"


def test_add_all_items_to_cart(logged_in_inventory_page: InventoryPage):
    """
    Test adding all available items to cart.
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Get all product names
    product_names = inventory_page.get_product_names()
    
    # Add all products
    for product_name in product_names:
        inventory_page.add_to_cart_by_name(product_name)
    
    # Verify cart count equals number of products
    assert inventory_page.get_cart_count() == len(product_names), \
        f"Cart should have {len(product_names)} items"


@pytest.mark.smoke
def test_sort_products_price_low_to_high(logged_in_inventory_page: InventoryPage):
    """
    Test sorting products by price (low to high).
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Sort by price low to high
    inventory_page.sort_products("Price (low to high)")
    
    # Get prices and verify they are sorted
    prices = inventory_page.get_product_prices()
    assert prices == sorted(prices), "Products should be sorted by price (low to high)"


@pytest.mark.smoke
def test_sort_products_price_high_to_low(logged_in_inventory_page: InventoryPage):
    """
    Test sorting products by price (high to low).
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Sort by price high to low
    inventory_page.sort_products("Price (high to low)")
    
    # Get prices and verify they are sorted descending
    prices = inventory_page.get_product_prices()
    assert prices == sorted(prices, reverse=True), \
        "Products should be sorted by price (high to low)"


def test_sort_products_name_a_to_z(logged_in_inventory_page: InventoryPage):
    """
    Test sorting products by name (A to Z).
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Sort by name A to Z (default)
    inventory_page.sort_products("Name (A to Z)")
    
    # Get names and verify they are sorted
    names = inventory_page.get_product_names()
    assert names == sorted(names), "Products should be sorted by name (A to Z)"


def test_sort_products_name_z_to_a(logged_in_inventory_page: InventoryPage):
    """
    Test sorting products by name (Z to A).
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Sort by name Z to A
    inventory_page.sort_products("Name (Z to A)")
    
    # Get names and verify they are sorted descending
    names = inventory_page.get_product_names()
    assert names == sorted(names, reverse=True), \
        "Products should be sorted by name (Z to A)"


@pytest.mark.regression
def test_product_count_displayed(logged_in_inventory_page: InventoryPage):
    """
    Test that all 6 products are displayed on inventory page.
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    product_names = inventory_page.get_product_names()
    assert len(product_names) == 6, "Inventory should display 6 products"


@pytest.mark.regression
def test_all_products_have_prices(logged_in_inventory_page: InventoryPage):
    """
    Test that all products have valid prices displayed.
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    prices = inventory_page.get_product_prices()
    
    # Verify we have 6 prices
    assert len(prices) == 6, "Should have 6 product prices"
    
    # Verify all prices are positive
    for price in prices:
        assert price > 0, f"Price {price} should be greater than 0"


def test_navigate_to_cart_from_inventory(logged_in_inventory_page: InventoryPage):
    """
    Test navigation to cart page from inventory.
    
    Args:
        logged_in_inventory_page: Logged in inventory page fixture
    """
    inventory_page = logged_in_inventory_page
    
    # Go to cart
    inventory_page.go_to_cart()
    
    # Verify URL changed to cart
    current_url = inventory_page.get_current_url()
    assert "cart.html" in current_url, "Should navigate to cart page"

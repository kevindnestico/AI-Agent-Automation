"""
Inventory Page Object Model for Saucedemo.
"""
from typing import List
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Page object for the Saucedemo inventory/products page."""
    
    def __init__(self, page: Page):
        """
        Initialize the inventory page.
        
        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self._page_title: Locator = page.locator(".title")
        self._cart_badge: Locator = page.locator(".shopping_cart_badge")
        self._cart_link: Locator = page.locator(".shopping_cart_link")
        self._inventory_items: Locator = page.locator(".inventory_item")
    
    def verify_inventory_page_loaded(self) -> None:
        """Verify that the inventory page has loaded successfully."""
        expect(self._page_title).to_be_visible()
        expect(self._page_title).to_have_text("Products")
        self.wait_for_url(f"{self.base_url}/inventory.html")
    
    def add_to_cart_by_name(self, product_name: str) -> None:
        """
        Add a product to cart by its name.
        
        Args:
            product_name: Name of the product to add to cart
        """
        # Find the inventory item containing the product name
        item = self.page.locator(".inventory_item").filter(
            has=self.page.get_by_text(product_name, exact=True)
        )
        
        # Click the "Add to cart" button for this item
        add_button = item.get_by_role("button", name="Add to cart")
        expect(add_button).to_be_visible()
        add_button.click()
        
        # Verify button text changed to "Remove"
        remove_button = item.get_by_role("button", name="Remove")
        expect(remove_button).to_be_visible()
    
    def remove_from_cart_by_name(self, product_name: str) -> None:
        """
        Remove a product from cart by its name.
        
        Args:
            product_name: Name of the product to remove from cart
        """
        item = self.page.locator(".inventory_item").filter(
            has=self.page.get_by_text(product_name, exact=True)
        )
        
        remove_button = item.get_by_role("button", name="Remove")
        expect(remove_button).to_be_visible()
        remove_button.click()
    
    def go_to_cart(self) -> None:
        """Navigate to the shopping cart page."""
        self._cart_link.click()
        self.wait_for_url(f"{self.base_url}/cart.html")
    
    def get_cart_count(self) -> int:
        """
        Get the number of items in the cart badge.
        
        Returns:
            int: Number of items in cart, 0 if badge not visible
        """
        if self._cart_badge.is_visible():
            return int(self._cart_badge.inner_text())
        return 0
    
    def get_product_prices(self) -> List[float]:
        """
        Get all product prices on the inventory page.
        
        Returns:
            List[float]: List of product prices
        """
        price_elements = self.page.locator(".inventory_item_price").all()
        prices = []
        
        for price_element in price_elements:
            price_text = price_element.inner_text()
            # Remove dollar sign and convert to float
            price = float(price_text.replace("$", ""))
            prices.append(price)
        
        return prices
    
    def get_product_names(self) -> List[str]:
        """
        Get all product names on the inventory page.
        
        Returns:
            List[str]: List of product names
        """
        name_elements = self.page.locator(".inventory_item_name").all()
        return [name.inner_text() for name in name_elements]
    
    def sort_products(self, sort_option: str) -> None:
        """
        Sort products by the given option.
        
        Args:
            sort_option: Sort option text (e.g., "Price (low to high)")
        """
        sort_dropdown = self.page.locator(".product_sort_container")
        sort_dropdown.select_option(label=sort_option)

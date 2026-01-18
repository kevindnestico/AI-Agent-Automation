"""
Cart Page Object Model for Saucedemo.
"""
from typing import List
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class CartPage(BasePage):
    """Page object for the Saucedemo shopping cart page."""
    
    def __init__(self, page: Page):
        """
        Initialize the cart page.
        
        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self._page_title: Locator = page.locator(".title")
        self._checkout_button: Locator = page.get_by_role("button", name="Checkout")
        self._continue_shopping_button: Locator = page.get_by_role("button", name="Continue Shopping")
        self._cart_items: Locator = page.locator(".cart_item")
    
    def verify_cart_page_loaded(self) -> None:
        """Verify that the cart page has loaded successfully."""
        expect(self._page_title).to_be_visible()
        expect(self._page_title).to_have_text("Your Cart")
        self.wait_for_url(f"{self.base_url}/cart.html")
    
    def remove_item(self, product_name: str) -> None:
        """
        Remove an item from the cart by product name.
        
        Args:
            product_name: Name of the product to remove
        """
        # Find the cart item containing the product name
        item = self.page.locator(".cart_item").filter(
            has=self.page.get_by_text(product_name, exact=True)
        )
        
        # Click the remove button for this item
        remove_button = item.get_by_role("button", name="Remove")
        expect(remove_button).to_be_visible()
        remove_button.click()
        
        # Verify item is removed (item should not exist anymore)
        expect(item).not_to_be_visible()
    
    def proceed_to_checkout(self) -> None:
        """Proceed to the checkout information page."""
        expect(self._checkout_button).to_be_visible()
        self._checkout_button.click()
        self.wait_for_url(f"{self.base_url}/checkout-step-one.html")
    
    def continue_shopping(self) -> None:
        """Return to the inventory page."""
        self._continue_shopping_button.click()
        self.wait_for_url(f"{self.base_url}/inventory.html")
    
    def get_cart_item_count(self) -> int:
        """
        Get the number of items in the cart.
        
        Returns:
            int: Number of items in cart
        """
        return self._cart_items.count()
    
    def get_cart_item_names(self) -> List[str]:
        """
        Get names of all items in the cart.
        
        Returns:
            List[str]: List of product names in cart
        """
        name_elements = self.page.locator(".inventory_item_name").all()
        return [name.inner_text() for name in name_elements]
    
    def get_cart_item_prices(self) -> List[float]:
        """
        Get prices of all items in the cart.
        
        Returns:
            List[float]: List of product prices in cart
        """
        price_elements = self.page.locator(".inventory_item_price").all()
        prices = []
        
        for price_element in price_elements:
            price_text = price_element.inner_text()
            price = float(price_text.replace("$", ""))
            prices.append(price)
        
        return prices
    
    def is_cart_empty(self) -> bool:
        """
        Check if the cart is empty.
        
        Returns:
            bool: True if cart is empty, False otherwise
        """
        return self._cart_items.count() == 0

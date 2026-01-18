"""
Checkout Overview Page Object Model for Saucedemo.
"""
from typing import List, Dict
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class CheckoutOverviewPage(BasePage):
    """Page object for the Saucedemo checkout overview page."""
    
    def __init__(self, page: Page):
        """
        Initialize the checkout overview page.
        
        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self._page_title: Locator = page.locator(".title")
        self._finish_button: Locator = page.get_by_role("button", name="Finish")
        self._cancel_button: Locator = page.get_by_role("button", name="Cancel")
        self._cart_items: Locator = page.locator(".cart_item")
        self._subtotal: Locator = page.locator(".summary_subtotal_label")
        self._tax: Locator = page.locator(".summary_tax_label")
        self._total: Locator = page.locator(".summary_total_label")
    
    def verify_checkout_overview_page_loaded(self) -> None:
        """Verify that the checkout overview page has loaded successfully."""
        expect(self._page_title).to_be_visible()
        expect(self._page_title).to_have_text("Checkout: Overview")
        self.wait_for_url(f"{self.base_url}/checkout-step-two.html")
    
    def finish(self) -> None:
        """Complete the checkout process."""
        expect(self._finish_button).to_be_visible()
        expect(self._finish_button).to_be_enabled()
        self._finish_button.click()
        self.wait_for_url(f"{self.base_url}/checkout-complete.html")
    
    def cancel_checkout(self) -> None:
        """Cancel checkout and return to inventory page."""
        self._cancel_button.click()
        self.wait_for_url(f"{self.base_url}/inventory.html")
    
    def get_item_names(self) -> List[str]:
        """
        Get names of all items in the checkout overview.
        
        Returns:
            List[str]: List of product names
        """
        name_elements = self.page.locator(".inventory_item_name").all()
        return [name.inner_text() for name in name_elements]
    
    def get_item_count(self) -> int:
        """
        Get the number of items in the checkout overview.
        
        Returns:
            int: Number of items
        """
        return self._cart_items.count()
    
    def get_payment_summary(self) -> Dict[str, float]:
        """
        Get the payment summary details.
        
        Returns:
            Dict[str, float]: Dictionary with subtotal, tax, and total amounts
        """
        subtotal_text = self._subtotal.inner_text()
        tax_text = self._tax.inner_text()
        total_text = self._total.inner_text()
        
        # Extract numeric values (format: "Item total: $XXX.XX")
        subtotal = float(subtotal_text.split("$")[1])
        tax = float(tax_text.split("$")[1])
        total = float(total_text.split("$")[1])
        
        return {
            "subtotal": subtotal,
            "tax": tax,
            "total": total
        }
    
    def verify_payment_summary_visible(self) -> None:
        """Verify that payment summary elements are visible."""
        expect(self._subtotal).to_be_visible()
        expect(self._tax).to_be_visible()
        expect(self._total).to_be_visible()
    
    def get_payment_information(self) -> str:
        """
        Get the payment information text.
        
        Returns:
            str: Payment information text
        """
        payment_info = self.page.locator(".summary_value_label").first
        expect(payment_info).to_be_visible()
        return payment_info.inner_text()
    
    def get_shipping_information(self) -> str:
        """
        Get the shipping information text.
        
        Returns:
            str: Shipping information text
        """
        shipping_info = self.page.locator(".summary_value_label").last
        expect(shipping_info).to_be_visible()
        return shipping_info.inner_text()

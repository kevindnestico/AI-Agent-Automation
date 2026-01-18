"""
Checkout Complete Page Object Model for Saucedemo.
"""
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    """Page object for the Saucedemo checkout complete page."""
    
    def __init__(self, page: Page):
        """
        Initialize the checkout complete page.
        
        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self._page_title: Locator = page.locator(".title")
        self._complete_header: Locator = page.locator(".complete-header")
        self._complete_text: Locator = page.locator(".complete-text")
        self._back_home_button: Locator = page.get_by_role("button", name="Back Home")
        self._pony_express_image: Locator = page.locator(".pony_express")
    
    def verify_checkout_complete_page_loaded(self) -> None:
        """Verify that the checkout complete page has loaded successfully."""
        expect(self._page_title).to_be_visible()
        expect(self._page_title).to_have_text("Checkout: Complete!")
        self.wait_for_url(f"{self.base_url}/checkout-complete.html")
    
    def get_thank_you_message(self) -> str:
        """
        Get the thank you message/header.
        
        Returns:
            str: Thank you message text
        """
        expect(self._complete_header).to_be_visible()
        return self._complete_header.inner_text()
    
    def get_complete_text(self) -> str:
        """
        Get the order completion message text.
        
        Returns:
            str: Completion message text
        """
        expect(self._complete_text).to_be_visible()
        return self._complete_text.inner_text()
    
    def go_back_home(self) -> None:
        """Navigate back to the inventory page."""
        expect(self._back_home_button).to_be_visible()
        self._back_home_button.click()
        self.wait_for_url(f"{self.base_url}/inventory.html")
    
    def is_success_image_visible(self) -> bool:
        """
        Check if the success image (pony express) is visible.
        
        Returns:
            bool: True if image is visible, False otherwise
        """
        return self._pony_express_image.is_visible()
    
    def verify_order_complete(self) -> None:
        """Verify that the order has been completed successfully."""
        expect(self._complete_header).to_have_text("Thank you for your order!")
        expect(self._complete_text).to_be_visible()
        expect(self._pony_express_image).to_be_visible()

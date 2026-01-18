"""
Checkout Information Page Object Model for Saucedemo.
"""
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class CheckoutInfoPage(BasePage):
    """Page object for the Saucedemo checkout information page."""
    
    def __init__(self, page: Page):
        """
        Initialize the checkout info page.
        
        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self._page_title: Locator = page.locator(".title")
        self._first_name_input: Locator = page.get_by_placeholder("First Name")
        self._last_name_input: Locator = page.get_by_placeholder("Last Name")
        self._postal_code_input: Locator = page.get_by_placeholder("Zip/Postal Code")
        self._continue_button: Locator = page.get_by_role("button", name="Continue")
        self._cancel_button: Locator = page.get_by_role("button", name="Cancel")
        self._error_message: Locator = page.locator("[data-test='error']")
    
    def verify_checkout_info_page_loaded(self) -> None:
        """Verify that the checkout info page has loaded successfully."""
        expect(self._page_title).to_be_visible()
        expect(self._page_title).to_have_text("Checkout: Your Information")
        self.wait_for_url(f"{self.base_url}/checkout-step-one.html")
    
    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        """
        Fill in checkout information form.
        
        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            postal_code: Customer's postal/zip code
        """
        expect(self._first_name_input).to_be_visible()
        self._first_name_input.fill(first_name)
        self._last_name_input.fill(last_name)
        self._postal_code_input.fill(postal_code)
    
    def continue_to_overview(self) -> None:
        """Continue to the checkout overview page."""
        expect(self._continue_button).to_be_enabled()
        self._continue_button.click()
        self.wait_for_url(f"{self.base_url}/checkout-step-two.html")
    
    def cancel_checkout(self) -> None:
        """Cancel checkout and return to cart page."""
        self._cancel_button.click()
        self.wait_for_url(f"{self.base_url}/cart.html")
    
    def get_error_message(self) -> str:
        """
        Get the error message displayed on form validation failure.
        
        Returns:
            str: Error message text
        """
        expect(self._error_message).to_be_visible()
        return self._error_message.inner_text()
    
    def is_error_displayed(self) -> bool:
        """
        Check if error message is displayed.
        
        Returns:
            bool: True if error is visible, False otherwise
        """
        return self._error_message.is_visible()

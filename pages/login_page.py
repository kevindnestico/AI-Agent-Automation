"""
Login Page Object Model for Saucedemo.
"""
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object for the Saucedemo login page."""
    
    def __init__(self, page: Page):
        """
        Initialize the login page.
        
        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self._username_input: Locator = page.get_by_placeholder("Username")
        self._password_input: Locator = page.get_by_placeholder("Password")
        self._login_button: Locator = page.get_by_role("button", name="Login")
        self._error_message: Locator = page.locator("[data-test='error']")
    
    def navigate(self) -> None:
        """Navigate to the login page."""
        self.navigate_to("/")
    
    def login(self, username: str, password: str) -> None:
        """
        Perform login with given credentials.
        
        Args:
            username: Username to login with
            password: Password to login with
        """
        self._username_input.fill(username)
        self._password_input.fill(password)
        self._login_button.click()
    
    def get_error_message(self) -> str:
        """
        Get the error message displayed on login failure.
        
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
    
    def verify_login_page_loaded(self) -> None:
        """Verify that the login page has loaded successfully."""
        expect(self._username_input).to_be_visible()
        expect(self._password_input).to_be_visible()
        expect(self._login_button).to_be_visible()

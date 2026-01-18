"""
Base Page class with common functionality for all page objects.
"""
from playwright.sync_api import Page, expect


class BasePage:
    """Base class for all page objects with common methods and properties."""
    
    def __init__(self, page: Page):
        """
        Initialize the base page.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.base_url = "https://www.saucedemo.com"
    
    def navigate_to(self, path: str = "") -> None:
        """
        Navigate to a specific path on the base URL.
        
        Args:
            path: URL path to navigate to (default: "")
        """
        url = f"{self.base_url}{path}"
        self.page.goto(url)
    
    def get_current_url(self) -> str:
        """
        Get the current page URL.
        
        Returns:
            str: Current page URL
        """
        return self.page.url
    
    def wait_for_url(self, url: str, timeout: int = 5000) -> None:
        """
        Wait for the page to navigate to a specific URL.
        
        Args:
            url: Expected URL
            timeout: Maximum wait time in milliseconds (default: 5000)
        """
        self.page.wait_for_url(url, timeout=timeout)

"""
Pytest configuration and fixtures for Saucedemo tests.
"""
import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext


@pytest.fixture(scope="function")
def browser() -> Browser:
    """
    Create and return a Chromium browser instance.
    
    Yields:
        Browser: Playwright browser instance
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            slow_mo=500
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """
    Create a new browser context with custom viewport.
    
    Args:
        browser: Browser instance from browser fixture
        
    Yields:
        BrowserContext: Isolated browser context
    """
    context = browser.new_context(
        viewport={"width": 1280, "height": 800}
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """
    Create a new page in the browser context.
    
    Args:
        context: Browser context from context fixture
        
    Yields:
        Page: Playwright page instance
    """
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def authenticated_page(page: Page) -> Page:
    """
    Create a page that's already logged in to Saucedemo.
    
    Args:
        page: Page instance from page fixture
        
    Yields:
        Page: Authenticated page instance
    """
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    yield page

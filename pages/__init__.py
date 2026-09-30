"""
Page Object Model package for Saucedemo automation.
"""

from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.checkout_info_page import CheckoutInfoPage
from pages.checkout_overview_page import CheckoutOverviewPage, PaymentSummary
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage

__all__ = [
    "BasePage",
    "CartPage",
    "CheckoutCompletePage",
    "CheckoutInfoPage",
    "CheckoutOverviewPage",
    "InventoryPage",
    "LoginPage",
    "PaymentSummary",
    "ProductDetailPage",
]

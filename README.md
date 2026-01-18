# Saucedemo Page Object Model + Claude + Python + Playwright

This project implements a complete and robust **Page Object Model (POM)** for automating tests on [Saucedemo](https://www.saucedemo.com/) using **Python** and **Playwright Sync API**.

## Implemented Page Objects

### BasePage
Common functionality for all Page Objects:

- Navigation
- Get current URL
- Wait for URL

### LoginPage
- `login(username, password)` – Perform login
- `get_error_message()` – Get error message
- `verify_login_page_loaded()` – Verify page is loaded

### InventoryPage
- `add_to_cart_by_name(product_name)`
- `remove_from_cart_by_name(product_name)`
- `go_to_cart()`
- `get_product_prices()`
- `get_product_names()`
- `sort_products(sort_option)`
- `get_cart_count()`

### CartPage
- `remove_item(product_name)`
- `proceed_to_checkout()`
- `get_cart_item_count()`
- `get_cart_item_names()`
- `is_cart_empty()`

### CheckoutInfoPage
- `fill_info(first_name, last_name, postal_code)`
- `continue_to_overview()`
- `get_error_message()`

### CheckoutOverviewPage
- `finish()`
- `get_payment_summary()`
- `get_item_count()`

### CheckoutCompletePage
- `get_thank_you_message()`
- `verify_order_complete()`
- `go_back_home()`

## Technical Features

- **Robust locators** using:
  - `get_by_role()`
  - `get_by_text()`
  - `get_by_placeholder()`
  - `get_by_test_id()`
- **Playwright assertions**:
  - `expect(locator).to_be_visible()`
  - `expect(locator).to_have_text()`
  - `expect(locator).to_be_enabled()`
  - `expect(locator).not_to_be_visible()`
- Full **type hints** on classes and methods
- Complete **Google-style docstrings**

## Installation

```bash
# Install dependencies
pip install playwright pytest pytest-playwright

# Install browsers
playwright install chromium

Running TestsRun all testsbash

pytest

Run specific test filesbash

pytest tests/test_login.py -v
pytest tests/test_inventory.py -v
pytest tests/test_cart.py -v
pytest tests/test_checkout_happy_path.py -v
pytest tests/test_checkout_negative.py -v
pytest tests/test_complete_purchase.py -v

Run single testbash

pytest tests/test_checkout_happy_path.py::test_checkout_happy_path -v

Run in headed mode (see browser)bash

pytest tests/test_login.py -v --headed

Run by markersbash

# Smoke tests only
pytest -m smoke -v

# Regression tests only
pytest -m regression -v

# Exclude slow tests
pytest -m "not slow" -v

Parallel execution (requires pytest-xdist)bash

pytest -n auto
pytest -n 4

HTML report (requires pytest-html)bash

pytest --html=reports/report.html --self-contained-html

Coverage report (requires pytest-cov)bash

pytest --cov=pages --cov-report=html

Happy Testing! 


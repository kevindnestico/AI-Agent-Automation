# Saucedemo E2E Automation — Playwright + Python + Claude

[![E2E Tests](https://github.com/kevindnestico/AI-Agent-Automation/actions/workflows/tests.yml/badge.svg)](https://github.com/kevindnestico/AI-Agent-Automation/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/Allure-report-orange?logo=qameta)](https://kevindnestico.github.io/AI-Agent-Automation/)
![Python](https://img.shields.io/badge/python-3.11+-blue?logo=python)
![Playwright](https://img.shields.io/badge/playwright-1.63-2EAD33?logo=playwright)
[![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64)](https://docs.astral.sh/ruff/)

End-to-end test framework for [Saucedemo](https://www.saucedemo.com/) built with **Playwright (sync API)**,
**pytest** and the **Page Object Model**, running cross-browser in **GitHub Actions** with an **Allure** report
published to GitHub Pages. Failed tests can be diagnosed automatically by **Claude**, which returns a structured
root-cause analysis attached to the report.

**144 tests** covering login, inventory, product detail, cart, checkout, order totals, session security,
accessibility, network behavior and visual regression, run on Chromium, Firefox and WebKit.

---

## Highlights

| | |
|---|---|
| 🔐 **Login once, reuse everywhere** | Each user logs in through the UI once per worker; the session is saved with `storage_state` and injected into every test's browser context. Refreshed automatically before Saucedemo's 10-minute cookie expires. |
| 🔗 **Chained fixtures** | `logged_in_page → inventory_page → cart_page → checkout_info_page → checkout_overview_page`. Each test asks for the state it needs, nothing more. |
| ⚡ **UI-free preconditions** | Cart contents are seeded through `localStorage`, so checkout tests don't depend on the add-to-cart UI (which has its own tests). |
| 🐞 **Known-bugs registry** | Saucedemo's special users have intentional defects. Tests assert the *correct* behavior for every user, and affected users are marked as **strict xfail** from a single registry ([`data/known_bugs.py`](data/known_bugs.py)). If a bug gets fixed, the XPASS fails the build so the registry stays accurate. |
| 🤖 **AI failure analysis** | `pytest --ai-analysis` sends the failing test's source, error, URL, ARIA snapshot and screenshot to Claude and attaches a structured diagnosis (category, root cause, evidence, fix, confidence) to Allure. |
| 👁️ **Baseline-free visual regression** | Each user's inventory page is compared pixel by pixel with `standard_user`'s, captured in the same run, so there are no OS- or browser-specific baseline images to maintain. |
| ♿ **Accessibility** | axe-core scans on every main page; the build fails on critical and serious violations, and the full report is attached to Allure. |
| 🌐 **Network checks** | Console and HTTP errors during a full purchase, the purchase flow with images blocked (`page.route`), cache headers, and a documented hosting bug (deep links return HTTP 404). |
| 🧱 **Stable by design** | Every page object waits for its URL **and** rendered title before reading data, which fixed race conditions in the original suite. The full suite passes repeatedly across three browsers with no flaky tests. |

## Tech stack

Python 3.11 · pytest 9 · Playwright 1.63 · pytest-xdist · pytest-rerunfailures · Allure · axe-core ·
Anthropic Python SDK (Claude) · Pillow · Ruff · pre-commit · GitHub Actions

## Project structure

```
├── ai/                     # Claude failure analyzer (prompt, structured output model, client)
├── config/                 # Settings from env/.env, Allure failure categories
├── data/                   # Users, product catalog, customers, messages, known bugs, login cases (JSON)
├── pages/                  # Page Objects (+ components/header.py shared by all pages)
├── tests/                  # E2E tests by feature, tests/unit for framework code
├── utils/                  # Screenshot comparison helper
├── conftest.py             # Fixtures, storage_state auth, Allure and AI failure hooks
├── pytest.ini              # Markers, base_url, Allure output, strict xfail
└── .github/workflows/      # CI: lint → tests (3 browsers) → Allure report on GitHub Pages
```

## Test coverage

| Area | File | What it checks |
|---|---|---|
| Login | `test_login.py` | Valid users, data-driven negative cases from JSON (incl. SQL injection, case sensitivity), login SLA, error dismissal |
| Session & security | `test_session.py` | Protected routes redirect to login, logout clears the session, back button after logout, reload, reset app state |
| Inventory | `test_inventory.py` | Add/remove, the 4 sort options, catalog names and prices |
| Product detail | `test_product_detail.py` | Every product matches the catalog, add/remove from detail, state shared with inventory, direct links |
| Cart | `test_cart.py` | Contents, removal, badge, persistence, navigation |
| Checkout | `test_checkout_*.py` | Happy path, required fields, cancel flows, unusual input, subtotal / 8% tax / total for several carts |
| End-to-end | `test_complete_purchase_full.py` | Full purchases driven only through the UI |
| Special users | `test_special_users.py` | Images, sorting, prices, add/remove, checkout form and order completion for all 5 login-capable users |
| Visual | `test_visual.py` | Cross-user pixel comparison against `standard_user` |
| Accessibility | `test_accessibility.py` | axe-core on login, inventory, detail, cart and checkout |
| Network | `test_network.py` | Console/HTTP errors, images blocked, cache headers, deep-link status |
| Framework | `tests/unit/` | AI analyzer request, caching, budget and error handling (fake client, no API calls) |

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
```

```bash
pip install -r requirements-dev.txt
```

```bash
playwright install chromium firefox webkit
```

Optional: `cp .env.example .env` to override the password, timeouts or AI settings.

## Running tests

```bash
pytest
```

```bash
pytest -n auto --browser chromium --browser firefox --browser webkit
```

```bash
pytest -m smoke
```

```bash
pytest tests/test_special_users.py -rxX
```

```bash
pytest tests/test_login.py --headed --slowmo 300
```

```bash
pytest --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure
```

```bash
pytest --base-url https://staging.example.com
```

Markers: `smoke`, `regression`, `known_bug`, `visual`, `a11y`, `unit`.

## Allure report

Results are written to `allure-results/` on every run, with environment info and failure categories
(known bugs, timeouts, locator issues, assertion failures, infrastructure).

```bash
allure serve allure-results
```

CI merges the results from all browsers, keeps the trend history and publishes the report to
**https://kevindnestico.github.io/AI-Agent-Automation/**.

## AI failure analysis with Claude

```bash
ANTHROPIC_API_KEY=sk-ant-... pytest --ai-analysis
```

For each failed test (after any retries), the hook in `conftest.py` captures the test source, the error and
traceback, the page URL, an ARIA snapshot and a screenshot **before the page is closed**, and
[`ai/failure_analyzer.py`](ai/failure_analyzer.py) asks Claude for a structured diagnosis:

```json
{
  "category": "locator_changed",
  "summary": "Checkout button data-test was renamed",
  "root_cause": "get_by_test_id('checkout') matches nothing; the ARIA snapshot shows a button named 'Proceed'.",
  "evidence": ["waiting for get_by_test_id(\"checkout\")", "- button \"Proceed\""],
  "suggested_fix": "Update CartPage.checkout_button to the new data-test value.",
  "confidence": "high"
}
```

Categories: `product_bug`, `test_bug`, `locator_changed`, `timing_flakiness`, `environment`, `unknown`.
The diagnosis is attached to the Allure test (markdown and JSON), tagged `ai:<category>`, and printed in the
terminal report.

Implementation notes:

- **Structured outputs** with a Pydantic model (`messages.parse`), so the response is always valid JSON.
- **Prompt caching**: the system prompt is static and includes the known-bugs registry, so it is cached across failures.
- **Safe by default**: off unless `--ai-analysis` is passed; at most `AI_ANALYSIS_MAX` analyses per run; never
  analyzes intermediate reruns; API problems are logged and never change the test result.
- Configurable through `AI_ANALYSIS_MODEL` (default `claude-opus-5-5`) and `AI_ANALYSIS_EFFORT` (default `medium`).
- In CI it runs only when the `ANTHROPIC_API_KEY` repository secret is set.

## CI/CD

[`.github/workflows/tests.yml`](.github/workflows/tests.yml) runs on every push and pull request, on a weekday
schedule to catch changes in the site under test, and on demand:

1. **Lint**: `ruff check` and `ruff format --check`.
2. **Tests**: a matrix of Chromium, Firefox and WebKit, parallel with xdist, one rerun for network flakiness.
   Traces, screenshots and videos are uploaded only for failures.
3. **Report** (on `master`): merges the Allure results, keeps the history and publishes to GitHub Pages.

## Design decisions

- **Why `data-test` locators?** Saucedemo exposes them on every interactive element. They are stable and
  independent of copy and styling. `get_by_role` is still used where the accessible name is the contract
  (e.g. the menu button).
- **Why wait for the title in `should_be_loaded()`?** Saucedemo is a SPA: the URL changes before React swaps the
  view, so reading items right after `wait_for_url` returned the previous page's data. The original suite had
  5 failing tests caused by this.
- **Why strict xfail instead of asserting the broken behavior?** The test documents the expected behavior, the
  report lists each known defect explicitly, and a fix is detected immediately.
- **Why not stored screenshot baselines?** They differ by OS, browser and font rendering, which makes CI
  (Linux) and local runs (macOS) disagree. Comparing against a reference captured in the same run avoids that.

"""
Registry of known defects in Saucedemo's special test users.

Saucedemo ships users with intentional bugs. Instead of writing tests that
assert the broken behavior, tests assert the *correct* behavior and are
parametrized across users; users affected by a known bug are marked as strict
``xfail`` with a clear reason. This way:

* the report lists every known defect explicitly (Allure category "Known bugs"),
* a bug that gets fixed turns the test into XPASS, which fails the run
  (``xfail_strict = true``) so the registry is kept up to date.
"""

from collections.abc import Iterable
from dataclasses import dataclass

import pytest

from data.users import LOGIN_CAPABLE_USERS, User


@dataclass(frozen=True)
class KnownBug:
    description: str
    affected_users: frozenset[User]


BROKEN_PRODUCT_IMAGES = KnownBug("Product images render the 404 placeholder", frozenset({User.PROBLEM, User.VISUAL}))
SORTING_BROKEN = KnownBug(
    "Sort dropdown does not reorder the products", frozenset({User.PROBLEM, User.ERROR, User.VISUAL})
)
CANNOT_ADD_SOME_PRODUCTS = KnownBug(
    "'Add to cart' does nothing for Bolt T-Shirt, Fleece Jacket and Red T-Shirt",
    frozenset({User.PROBLEM, User.ERROR}),
)
CANNOT_REMOVE_FROM_INVENTORY = KnownBug(
    "'Remove' button on the inventory page does nothing", frozenset({User.PROBLEM, User.ERROR})
)
CHECKOUT_FORM_CORRUPTS_INPUT = KnownBug(
    "Last name input overwrites first name (problem_user) or is not editable (error_user)",
    frozenset({User.PROBLEM, User.ERROR}),
)
FINISH_DOES_NOT_COMPLETE_ORDER = KnownBug("'Finish' button does not complete the order", frozenset({User.ERROR}))
WRONG_PRICES = KnownBug("Inventory shows random prices instead of catalog prices", frozenset({User.VISUAL}))
SLOW_LOGIN = KnownBug("Login takes ~5s, above the SLA", frozenset({User.PERFORMANCE_GLITCH}))
VISUAL_DIFFERENCES = KnownBug(
    "Inventory page looks different (misplaced elements, wrong images/prices)",
    frozenset({User.PROBLEM, User.VISUAL}),
)


def users_with_known_bugs(*bugs: KnownBug, users: Iterable[User] = LOGIN_CAPABLE_USERS) -> list:
    """Build ``pytest.param`` entries for ``users``, marking affected ones as strict xfail."""
    params = []
    for user in users:
        reasons = [bug.description for bug in bugs if user in bug.affected_users]
        marks = (
            [pytest.mark.known_bug, pytest.mark.xfail(reason="Known bug: " + "; ".join(reasons), raises=AssertionError)]
            if reasons
            else []
        )
        params.append(pytest.param(user, marks=marks, id=str(user)))
    return params

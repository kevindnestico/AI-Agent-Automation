"""Saucedemo product catalog used as the source of truth for assertions."""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, repr=False)
class Product:
    """A catalog product.

    Attributes:
        id: Internal id used by the app (``inventory-item.html?id=`` and localStorage cart).
        name: Display name.
        price: Unit price in USD.
    """

    id: int
    name: str
    price: float

    def __repr__(self) -> str:
        # Used by Allure step titles, e.g. "Add 'Sauce Labs Backpack' ($29.99) to cart".
        return f"'{self.name}' (${self.price})"

    @property
    def slug(self) -> str:
        """Suffix used in ``data-test`` attributes, e.g. ``add-to-cart-sauce-labs-backpack``."""
        return self.name.lower().replace(" ", "-")


BACKPACK = Product(4, "Sauce Labs Backpack", 29.99)
BIKE_LIGHT = Product(0, "Sauce Labs Bike Light", 9.99)
BOLT_T_SHIRT = Product(1, "Sauce Labs Bolt T-Shirt", 15.99)
FLEECE_JACKET = Product(5, "Sauce Labs Fleece Jacket", 49.99)
ONESIE = Product(2, "Sauce Labs Onesie", 7.99)
RED_T_SHIRT = Product(3, "Test.allTheThings() T-Shirt (Red)", 15.99)

ALL_PRODUCTS = (BACKPACK, BIKE_LIGHT, BOLT_T_SHIRT, FLEECE_JACKET, ONESIE, RED_T_SHIRT)


class SortOption(StrEnum):
    """Values of the product sort ``<select>``."""

    NAME_A_TO_Z = "az"
    NAME_Z_TO_A = "za"
    PRICE_LOW_TO_HIGH = "lohi"
    PRICE_HIGH_TO_LOW = "hilo"

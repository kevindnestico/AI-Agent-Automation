"""Customer data for the checkout form."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    """Shipping information entered on checkout step one."""

    first_name: str
    last_name: str
    postal_code: str


DEFAULT_CUSTOMER = Customer("Juan", "Perez", "12345")

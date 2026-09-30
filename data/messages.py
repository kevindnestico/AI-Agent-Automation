"""Expected user-facing messages."""


class LoginErrors:
    USERNAME_REQUIRED = "Epic sadface: Username is required"
    PASSWORD_REQUIRED = "Epic sadface: Password is required"
    INVALID_CREDENTIALS = "Epic sadface: Username and password do not match any user in this service"
    LOCKED_OUT = "Epic sadface: Sorry, this user has been locked out."

    @staticmethod
    def not_logged_in(path: str) -> str:
        return f"Epic sadface: You can only access '{path}' when you are logged in."


class CheckoutErrors:
    FIRST_NAME_REQUIRED = "Error: First Name is required"
    LAST_NAME_REQUIRED = "Error: Last Name is required"
    POSTAL_CODE_REQUIRED = "Error: Postal Code is required"


ORDER_COMPLETE_HEADER = "Thank you for your order!"

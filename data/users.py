"""Saucedemo user accounts."""

from enum import StrEnum


class User(StrEnum):
    """Usernames accepted by Saucedemo. All share the password from settings."""

    STANDARD = "standard_user"
    LOCKED_OUT = "locked_out_user"
    PROBLEM = "problem_user"
    PERFORMANCE_GLITCH = "performance_glitch_user"
    ERROR = "error_user"
    VISUAL = "visual_user"


# Users that can log in and reach the inventory page.
LOGIN_CAPABLE_USERS = tuple(user for user in User if user is not User.LOCKED_OUT)

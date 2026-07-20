class UserError(Exception):
    """Base exception for user domain."""


class DuplicateEmailError(UserError):
    """Raised when a user already exists."""


class InvalidEmailError(UserError):
    """Raised when email is invalid."""
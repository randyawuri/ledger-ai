class TransactionError(Exception):
    """Base transaction exception."""


class AccountNotFound(TransactionError):
    pass


class InvalidTransaction(TransactionError):
    pass


class InsufficientFunds(TransactionError):
    pass
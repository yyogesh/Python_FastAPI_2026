class DomainError(Exception):
    """A business rule said no. Knows nothing about HTTP."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """The thing asked for does not exist."""


class ConflictError(DomainError):
    """The request clashes with data that already exists."""


class BusinessRuleError(DomainError):
    """The request is well formed but breaks a business rule."""
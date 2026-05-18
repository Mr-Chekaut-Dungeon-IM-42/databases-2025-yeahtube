class DomainError(Exception):
    """Base exception for all domain/business errors."""


class NotFoundError(DomainError):
    """A domain error for 'not found' cases so Presentation can map to 404."""


class ConflictError(DomainError):
    """A domain error for conflicts (duplicates, invalid state transitions)."""


class UnauthorizedError(DomainError):
    """A domain error for authentication failures so Presentation can map to 401."""


class ForbiddenError(DomainError):
    """A domain error for permission failures so Presentation can map to 403."""


class GoneError(DomainError):
    """A domain error for 'resource is deleted / no longer available' (410)."""


class ValidationError(DomainError):
    """A domain error for input validation (400)."""

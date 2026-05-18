from __future__ import annotations

from dataclasses import dataclass

from app.domain.errors import DomainError


class DomainValidationError(DomainError):
    """Raised when a Value Object invariant is violated."""


@dataclass(frozen=True, slots=True)
class BoundedText:
    value: str
    min_length: int
    max_length: int

    def __post_init__(self) -> None:
        if self.value is None:
            raise DomainValidationError("Text value must not be None")
        if not isinstance(self.value, str):
            raise DomainValidationError("Text value must be a string")
        if len(self.value) < self.min_length:
            raise DomainValidationError(
                f"Text is too short: min_length={self.min_length}"
            )
        if len(self.value) > self.max_length:
            raise DomainValidationError(
                f"Text is too long: max_length={self.max_length}"
            )


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if self.value is None or not isinstance(self.value, str):
            raise DomainValidationError("Email must be a string")
        if "@" not in self.value or self.value.startswith("@") or self.value.endswith("@"):
            raise DomainValidationError("Email must contain a single '@' with local/domain parts")
        if len(self.value) > 64:
            raise DomainValidationError("Email too long")


@dataclass(frozen=True, slots=True)
class WatchedPercentage:
    value: float

    def __post_init__(self) -> None:
        if self.value is None:
            raise DomainValidationError("watched_percentage must not be None")
        if not (0.0 <= float(self.value) <= 1.0):
            raise DomainValidationError("watched_percentage must be between 0.0 and 1.0")
        object.__setattr__(self, "value", float(self.value))

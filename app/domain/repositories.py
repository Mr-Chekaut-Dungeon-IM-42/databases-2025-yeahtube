from __future__ import annotations

from typing import Protocol


class UserUniquenessChecker(Protocol):
    """DIP interface for factories that need DB-backed uniqueness checks."""

    def username_exists(self, username: str) -> bool: ...

    def email_exists(self, email: str) -> bool: ...

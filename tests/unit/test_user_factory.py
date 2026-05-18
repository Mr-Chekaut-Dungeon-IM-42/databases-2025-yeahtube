from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest

from app.domain.errors import DomainError
from app.domain.factories import UserFactory
from app.domain.value_objects import DomainValidationError


@dataclass
class FakeUniqueness:
    usernames: set[str]
    emails: set[str]

    def username_exists(self, username: str) -> bool:
        return username in self.usernames

    def email_exists(self, email: str) -> bool:
        return email in self.emails


def test_register_new_user_simple_invariants():
    factory = UserFactory(uniqueness=FakeUniqueness(usernames=set(), emails=set()))

    user = factory.register_new_user(
        username="user123",
        email="user@example.com",
        created_at=date(2026, 1, 1),
    )

    assert user.id == 0
    assert user.username.value == "user123"
    assert user.email.value == "user@example.com"


def test_register_new_user_invalid_email_raises_domain_error():
    factory = UserFactory(uniqueness=FakeUniqueness(usernames=set(), emails=set()))

    with pytest.raises(DomainValidationError):
        factory.register_new_user(
            username="user123",
            email="invalid",
            created_at=date(2026, 1, 1),
        )


def test_register_new_user_username_not_unique():
    factory = UserFactory(uniqueness=FakeUniqueness(usernames={"user123"}, emails=set()))

    with pytest.raises(DomainError):
        factory.register_new_user(
            username="user123",
            email="user@example.com",
            created_at=date(2026, 1, 1),
        )

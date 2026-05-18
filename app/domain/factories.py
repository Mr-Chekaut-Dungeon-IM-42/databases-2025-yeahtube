from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.errors import DomainError
from app.domain.models import UserD
from app.domain.repositories import UserUniquenessChecker
from app.domain.value_objects import BoundedText, Email


@dataclass(slots=True)
class UserFactory:
    """Creates domain users enforcing invariants.

    Simple invariants:
      - username length
      - email format

    Complex invariants (DB-backed):
      - username uniqueness
      - email uniqueness
    """

    uniqueness: UserUniquenessChecker

    def register_new_user(
        self,
        *,
        username: str,
        email: str,
        created_at: date,
        is_moderator: bool = False,
    ) -> UserD:
        username_vo = BoundedText(username, 3, 32)
        email_vo = Email(email)

        if self.uniqueness.username_exists(username_vo.value):
            raise DomainError("Username is already taken")
        if self.uniqueness.email_exists(email_vo.value):
            raise DomainError("Email is already registered")

        return UserD(
            id=0,
            username=username_vo,
            email=email_vo,
            created_at=created_at,
            is_moderator=is_moderator,
            is_deleted=False,
            is_banned=False,
        )

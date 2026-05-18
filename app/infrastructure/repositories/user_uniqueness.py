from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.domain.repositories import UserUniquenessChecker


class SqlAlchemyUserUniquenessChecker(UserUniquenessChecker):
    def __init__(self, db: Session):
        self._db = db

    def username_exists(self, username: str) -> bool:
        return (
            self._db.execute(select(User.id).where(User.username == username)).scalar_one_or_none()
            is not None
        )

    def email_exists(self, email: str) -> bool:
        return (
            self._db.execute(select(User.id).where(User.email == email)).scalar_one_or_none()
            is not None
        )

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import User


class AuthRepository:
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    @staticmethod
    def create_user(
        db: Session, username: str, email: str, hashed_password: str
    ) -> User:
        from datetime import date

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            created_at=date.today(),
            is_moderator=False,
            is_deleted=False,
            is_banned=False,
        )

        db.add(new_user)
        db.flush()
        return new_user

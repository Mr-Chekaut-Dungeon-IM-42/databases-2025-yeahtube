from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import User


class AuthRepository:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> dict | None:
        user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if user is None:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at,
            "is_moderator": user.is_moderator,
            "is_deleted": user.is_deleted,
            "is_banned": user.is_banned,
        }

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> dict | None:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user is None:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at,
            "is_moderator": user.is_moderator,
            "is_deleted": user.is_deleted,
            "is_banned": user.is_banned,
        }

    @staticmethod
    def create_user(
        db: Session, username: str, email: str, hashed_password: str
    ) -> dict:
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
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "created_at": new_user.created_at,
            "is_moderator": new_user.is_moderator,
            "is_deleted": new_user.is_deleted,
            "is_banned": new_user.is_banned,
        }

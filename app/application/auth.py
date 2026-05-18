from datetime import date

from sqlalchemy.orm import Session

from app.application.dto.auth import (
    LoginCommand,
    RegisterUserCommand,
    TokenView,
    UserView,
)
from app.domain.errors import (
    ForbiddenError,
    UnauthorizedError,
)
from app.domain.factories import UserFactory
from app.infrastructure.repositories.user_uniqueness import SqlAlchemyUserUniquenessChecker
from app.repositories.auth import AuthRepository
from app.utils.auth import create_access_token, get_password_hash, verify_password


class AuthService:
    @staticmethod
    def register_user(db: Session, cmd: RegisterUserCommand) -> UserView:
        checker = SqlAlchemyUserUniquenessChecker(db)
        factory = UserFactory(uniqueness=checker)

        _domain_user = factory.register_new_user(
            username=cmd.username,
            email=cmd.email,
            created_at=date.today(),
            is_moderator=False,
        )

        hashed_password = get_password_hash(cmd.password)

        try:
            new_user = AuthRepository.create_user(
                db=db,
                username=_domain_user.username.value,
                email=_domain_user.email.value,
                hashed_password=hashed_password,
            )
            db.commit()
            return UserView(**new_user)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def login_user(db: Session, cmd: LoginCommand) -> TokenView:
        user = AuthRepository.get_user_by_username(db, cmd.username)

        if not user:
            raise UnauthorizedError("Incorrect username")

        if not verify_password(cmd.password, user["hashed_password"]):
            raise UnauthorizedError("Incorrect password")

        if user["is_banned"]:
            raise ForbiddenError("User account is banned")

        if user["is_deleted"]:
            raise ForbiddenError("User account is deleted")

        access_token = create_access_token(
            data={
                "user_id": user["id"],
                "username": user["username"],
                "is_moderator": user["is_moderator"],
            }
        )

        return TokenView(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_user_info(user: dict) -> UserView:
        return UserView(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            is_moderator=user["is_moderator"],
            is_banned=user["is_banned"],
            created_at=user["created_at"],
        )

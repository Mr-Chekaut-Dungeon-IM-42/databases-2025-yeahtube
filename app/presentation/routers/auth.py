from fastapi import APIRouter, Depends, status
from app.db.session import DBDep
from app.dependencies import get_current_user
from app.application.dto.auth import LoginCommand, RegisterUserCommand
from app.application.auth import AuthService
from app.presentation.schemas.schemas import Token, UserLogin, UserOut, UserRegister

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: DBDep) -> UserOut:
    view = AuthService.register_user(
        db,
        RegisterUserCommand(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        ),
    )
    return UserOut(
        id=view.id,
        username=view.username,
        email=view.email,
        is_moderator=view.is_moderator,
        is_banned=view.is_banned,
        created_at=view.created_at,
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: DBDep) -> Token:
    token_view = AuthService.login_user(
        db,
        LoginCommand(username=credentials.username, password=credentials.password),
    )
    return Token(access_token=token_view.access_token, token_type=token_view.token_type)


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user=Depends(get_current_user),
) -> UserOut:
    view = AuthService.get_user_info(
        {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at,
            "is_moderator": current_user.is_moderator,
            "is_deleted": current_user.is_deleted,
            "is_banned": current_user.is_banned,
        }
    )
    return UserOut(
        id=view.id,
        username=view.username,
        email=view.email,
        is_moderator=view.is_moderator,
        is_banned=view.is_banned,
        created_at=view.created_at,
    )

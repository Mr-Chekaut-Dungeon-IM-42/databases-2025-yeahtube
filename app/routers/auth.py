from fastapi import APIRouter, Depends, status

from app.db.models import User
from app.db.session import DBDep
from app.dependencies import get_current_user
from app.schemas.schemas import Token, UserLogin, UserOut, UserRegister
from app.services.auth import AuthService

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: DBDep) -> UserOut:
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: DBDep) -> Token:
    return AuthService.login_user(db, credentials)


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserOut:
    return AuthService.get_user_info(current_user)

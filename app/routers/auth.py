from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.utils.auth import create_access_token, get_password_hash, verify_password
from app.db.models import User
from app.db.session import DBDep
from app.dependencies import get_current_user
from app.schemas.schemas import Token, UserLogin, UserOut, UserRegister

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: DBDep) -> UserOut:
    existing_user = db.execute(
        select(User).where(User.username == user_data.username)
    ).scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            created_at=date.today(),
            is_moderator=False,
            is_deleted=False,
            is_banned=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserOut(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_moderator=new_user.is_moderator,
            is_banned=new_user.is_banned,
            created_at=new_user.created_at
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: DBDep) -> Token:
    user = db.execute(
        select(User).where(User.username == credentials.username)
    ).scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned",
        )
    
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deleted",
        )
    
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "is_moderator": user.is_moderator
        }
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_moderator=current_user.is_moderator,
        is_banned=current_user.is_banned,
        created_at=current_user.created_at
    )

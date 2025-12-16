from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func, desc
from pydantic import BaseModel, EmailStr
from datetime import date

from app.db.models import User, Video, View, Subscription
from app.db.session import DBDep

router = APIRouter(prefix="/user")


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    is_moderator: bool = False


@router.get("/test")
async def test(db: DBDep):
    users = db.execute(select(User)).scalars().all()
    return {"users": [{"id": u.id, "username": u.username, "email": u.email, "created_at": u.created_at} for u in users]}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: DBDep):
    existing = db.execute(
        select(User).where(User.username == user_data.username)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    existing_email = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        created_at=date.today(),
        is_moderator=user_data.is_moderator
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "is_moderator": user.is_moderator
    }


@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int, db: DBDep, limit: int = 20):
    user_channel_views = (
        select(
            Video.channel_id,
            func.count(View.user_id).label('channel_view_count')
        )
        .join(Video, View.video_id == Video.id)
        .where(View.user_id == user_id)
        .group_by(Video.channel_id)
        .subquery()
    )
    
    subscriptions = (
        select(Subscription.channel_id)
        .where(Subscription.user_id == user_id)
        .subquery()
    )

    total_views = (
        select(
            View.video_id,
            func.count(View.user_id).label('total_view_count')
        )
        .group_by(View.video_id)
        .subquery()
    )

    query = (
        select(Video)
        .outerjoin(user_channel_views, Video.channel_id == user_channel_views.c.channel_id)
        .outerjoin(total_views, Video.id == total_views.c.video_id)
        .outerjoin(subscriptions, Video.channel_id == subscriptions.c.channel_id)
        .order_by(
            desc(func.coalesce(user_channel_views.c.channel_view_count, 0)),
            desc(subscriptions.c.channel_id.isnot(None)),
            desc(func.coalesce(total_views.c.total_view_count, 0))
        )
        .limit(limit)
    )
    
    videos = db.execute(query).scalars().all()
    
    return {
        "videos": [
            {
                "id": v.id,
                "title": v.title,
                "channel_id": v.channel_id,
                "created_at": v.uploaded_at
            }
            for v in videos
        ]
    }
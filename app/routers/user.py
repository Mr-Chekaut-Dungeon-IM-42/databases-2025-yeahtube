from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func, extract, desc
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date

from app.db.models import User, View, Video, Channel, Comment, Subscription
from app.db.session import DBDep

router = APIRouter(tags=["user"], prefix="/user")
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    is_moderator: bool = False

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    is_moderator: bool | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: date
    is_moderator: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)

class VideoResponse(BaseModel): 
    id: int
    title: str
    channel_id: int
    uploaded_at: date

    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=dict[str, list[UserResponse]])
async def get_all_users(db: DBDep):
    users = db.execute(select(User).where(User.is_deleted == False)).scalars().all()
    return {"users": users}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
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
    
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: DBDep):
    user = db.get(User, user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="User has been deleted")
    
    if user_data.username is not None:
        existing = db.execute(
            select(User).where(User.username == user_data.username, User.id != user_id)
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user.username = user_data.username
    
    if user_data.email is not None:
        existing_email = db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        ).scalar_one_or_none()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_data.email
    
    if user_data.is_moderator is not None:
        user.is_moderator = user_data.is_moderator
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(user_id: int, db: DBDep):
    user = db.get(User, user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="User already deleted")
    
    user.is_deleted = True
    db.commit()
    
    return None

@router.get("/{user_id}/recommendations", response_model=dict[str, list[VideoResponse]])
async def get_recommendations(user_id: int, db: DBDep, limit: int = 20):
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="User has been deleted")
    
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
        "videos": videos
    }

@router.get("/{user_id}/stats/views")
async def get_user_year_views(user_id: int, db: DBDep):
    current_year = datetime.now().year
    
    if not db.get(User, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    query = select(func.count(View.video_id)).where(
        View.user_id == user_id,
        extract('year', View.watched_at) == current_year
    )
    count = db.execute(query).scalar() or 0
    
    return {"user_id": user_id, "year": current_year, "total_views": count}

@router.get("/{user_id}/stats/favoriteCreator")
async def get_user_favorite_creator(user_id: int, db: DBDep):
    current_year = datetime.now().year

    if not db.get(User, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    query = (
        select(Channel.name, func.count(View.video_id).label("view_count"))
        .join(Video, View.video_id == Video.id)
        .join(Channel, Video.channel_id == Channel.id)
        .where(
            View.user_id == user_id,
            extract('year', View.watched_at) == current_year
        )
        .group_by(Channel.id)
        .order_by(desc("view_count"))
        .limit(1)
    )
    
    result = db.execute(query).first()
    
    if result:
        return {
            "user_id": user_id,
            "year": current_year,
            "favorite_creator": result.name,
            "videos_watched": result.view_count
        }
    else:
        return {
            "user_id": user_id,
            "year": current_year,
            "favorite_creator": None,
            "message": "No views found for this year"
    }

@router.get("/{user_id}/stats/reactions")
async def get_user_year_reactions(user_id: int, db: DBDep):
    """ Currently counts comments only """
    current_year = datetime.now().year

    if not db.get(User, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    query = select(func.count(Comment.id)).where(
        Comment.user_id == user_id,
        extract('year', Comment.commented_at) == current_year
    )
    count = db.execute(query).scalar() or 0
    
    return {
        "user_id": user_id, 
        "year": current_year, 
        "total_reactions": count
    }

@router.get("/{user_id}/stats/averageViewTime")
async def get_user_avg_view_time(user_id: int, db: DBDep):
    """ Currently returns nothing """
    if not db.get(User, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return {
        "user_id": user_id,
        "average_view_time_seconds": None
    }

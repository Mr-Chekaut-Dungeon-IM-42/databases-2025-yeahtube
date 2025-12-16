from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func, extract, desc

from app.db.models import User, View, Video, Channel, Comment
from app.db.session import DBDep

router = APIRouter(prefix="/user")


@router.get("/test")
async def test(db: DBDep):
    # user = User(
    #     id=1, username="Test", email="test@example.org", created_at="2025-07-07"
    # )
    # db.add(user)
    # db.commit()

    users = db.execute(select(User)).scalars().all()
    return {"users": [{"id": u.id, "username": u.username, "email": u.email, "created_at": u.created_at} for u in users]}

@router.get("/{user_id}/stats/views")
async def get_user_year_views(user_id: int, db: DBDep):
    current_year = datetime.now().year
    
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")

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
        raise HTTPException(status_code=404, detail="User not found")

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
        raise HTTPException(status_code=404, detail="User not found")

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
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "user_id": user_id,
        "average_view_time_seconds": None
}
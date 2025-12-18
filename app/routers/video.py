from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func
from datetime import date

from app.db.models import Video, Channel, View, Comment, User
from app.db.session import DBDep
from app.schemas.schemas import VideoCreate, VideoUpdate, VideoResponse,  VideoStatsResponse, VideoCommentsResponse, CommentResponse

router = APIRouter(tags=["video"], prefix="/video")

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: DBDep):
    video = db.get(Video, video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return video


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VideoResponse)
async def create_video(video_data: VideoCreate, db: DBDep):

    channel = db.get(Channel, video_data.channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    video = Video(
        title=video_data.title,
        description=video_data.description,
        uploaded_at=date.today(),
        channel_id=video_data.channel_id,
        is_active=video_data.is_active if video_data.is_active is not None else True,
        is_monetized=video_data.is_monetized if video_data.is_monetized is not None else False,
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    return video


@router.patch("/{video_id}", response_model=VideoResponse)
async def update_video(video_id: int, video_data: VideoUpdate, db: DBDep):
    video = db.get(Video, video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video_data.title is not None:
        video.title = video_data.title
    
    if video_data.description is not None:
        video.description = video_data.description
    
    if video_data.is_active is not None:
        video.is_active = video_data.is_active
    
    if video_data.is_monetized is not None:
        video.is_monetized = video_data.is_monetized
    
    db.commit()
    db.refresh(video)
    
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: int, db: DBDep):
    video = db.get(Video, video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    db.delete(video)
    db.commit()
    
    return None

@router.get("/{video_id}/stats", response_model=VideoStatsResponse)
async def get_video_stats(video_id: int, db: DBDep):
    video = db.get(Video, video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    stats = db.execute(
        select(
            func.count(View.user_id).label("total_views"),
            func.count(View.user_id).filter(View.reaction == "Liked").label("likes"),
            func.count(View.user_id).filter(View.reaction == "Disliked").label("dislikes")
        )
        .select_from(View)
        .where(View.video_id == video_id)
    ).one()
    
    total_views, likes, dislikes = stats
    
    total_comments = db.scalar(
        select(func.count(Comment.id)).where(Comment.video_id == video_id)
    ) or 0
    
    return VideoStatsResponse(
        video_id=video_id,
        title=video.title,
        total_views=total_views or 0,
        likes=likes or 0,
        dislikes=dislikes or 0,
        total_comments=total_comments
    )

@router.get("/{video_id}/comments")
async def get_video_comments(
    video_id: int, 
    db: DBDep,
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    video = db.get(Video, video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    skip = (page - 1) * limit

    total_count = db.scalar(
        select(func.count(Comment.id)).where(Comment.video_id == video_id)
    ) or 0

    comments = db.execute(
        select(Comment, User.username)
        .join(User, Comment.user_id == User.id)
        .where(Comment.video_id == video_id)
        .order_by(Comment.commented_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    
    return VideoCommentsResponse(
        video_id=video_id,
        title=video.title,
        comments=[
            CommentResponse(
                id=comment.id,
                comment_text=comment.comment_text,
                commented_at=comment.commented_at,
                user_id=comment.user_id,
                username=username
            )
            for comment, username in comments
        ],
        total_comments=total_count,
        page=page,
        limit=limit,
        total_pages=(total_count + limit - 1) // limit
    )
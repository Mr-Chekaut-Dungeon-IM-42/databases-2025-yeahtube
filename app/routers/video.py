from fastapi import APIRouter, status, Query
from app.db.session import DBDep
from app.services.video import VideoService
from app.schemas.schemas import (
    VideoCreate, VideoUpdate, VideoResponse, VideoWithCommentCreate,
    VideoStatsResponse, VideoWithCommentResponse
)

router = APIRouter(tags=["video"], prefix="/video")

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: DBDep):
    return VideoService.get_video(db, video_id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VideoResponse)
async def create_video(video_data: VideoCreate, db: DBDep):
    return VideoService.create_video(db, video_data)

@router.patch("/{video_id}", response_model=VideoResponse)
async def update_video(video_id: int, video_data: VideoUpdate, db: DBDep):
    return VideoService.update_video(db, video_id, video_data)

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: int, db: DBDep):
    VideoService.delete_video(db, video_id)
    return None

@router.get("/{video_id}/stats", response_model=VideoStatsResponse)
async def get_video_stats(video_id: int, db: DBDep):
    return VideoService.get_stats(db, video_id)

@router.get("/{video_id}/comments")
async def get_video_comments(
    video_id: int,
    db: DBDep,
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    return VideoService.get_comments(db, video_id, page, limit)

@router.post("/with-comment", status_code=status.HTTP_201_CREATED, response_model=VideoWithCommentResponse)
async def create_video_with_comment(video_data: VideoWithCommentCreate, db: DBDep):
    return VideoService.create_with_comment(db, video_data)
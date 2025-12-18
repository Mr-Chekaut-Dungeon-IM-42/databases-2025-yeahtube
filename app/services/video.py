from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Channel, Comment, User, Video
from app.repositories.video import VideoRepository
from app.schemas.schemas import (
    CommentResponse,
    VideoCommentsResponse,
    VideoCreate,
    VideoResponse,
    VideoStatsResponse,
    VideoUpdate,
    VideoWithCommentCreate,
    VideoWithCommentResponse,
)


class VideoService:
    @staticmethod
    def get_video(db: Session, video_id: int) -> VideoResponse:
        video = VideoRepository.get_by_id(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return VideoResponse.model_validate(video)

    @staticmethod
    def create_video(db: Session, video_data: VideoCreate) -> VideoResponse:
        channel = db.get(Channel, video_data.channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        video = Video(
            title=video_data.title,
            description=video_data.description,
            uploaded_at=date.today(),
            channel_id=video_data.channel_id,
            is_active=video_data.is_active
            if video_data.is_active is not None
            else True,
            is_monetized=video_data.is_monetized
            if video_data.is_monetized is not None
            else False,
        )
        return VideoResponse.model_validate(VideoRepository.create(db, video))

    @staticmethod
    def update_video(
        db: Session, video_id: int, video_data: VideoUpdate
    ) -> VideoResponse:
        video = VideoRepository.get_by_id(db, video_id, for_update=True)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
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
        return VideoResponse.model_validate(video)

    @staticmethod
    def delete_video(db: Session, video_id: int):
        video = VideoRepository.get_by_id(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        VideoRepository.delete(db, video)

    @staticmethod
    def get_stats(db: Session, video_id: int) -> VideoStatsResponse:
        video = VideoRepository.get_by_id(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        total_views, likes, dislikes, total_comments = VideoRepository.get_stats(
            db, video_id
        )
        return VideoStatsResponse(
            video_id=video_id,
            title=video.title,
            total_views=total_views or 0,
            likes=likes or 0,
            dislikes=dislikes or 0,
            total_comments=total_comments,
        )

    @staticmethod
    def get_comments(
        db: Session, video_id: int, page: int, limit: int
    ) -> VideoCommentsResponse:
        video = VideoRepository.get_by_id(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        skip = (page - 1) * limit
        total_count, comments = VideoRepository.get_comments(db, video_id, skip, limit)
        return VideoCommentsResponse(
            video_id=video_id,
            title=video.title,
            comments=[
                CommentResponse(
                    id=comment.id,
                    comment_text=comment.comment_text,
                    commented_at=comment.commented_at,
                    user_id=comment.user_id,
                    username=username,
                )
                for comment, username in comments
            ],
            total_comments=total_count,
            page=page,
            limit=limit,
            total_pages=(total_count + limit - 1) // limit,
        )

    @staticmethod
    def create_with_comment(
        db: Session, video_data: VideoWithCommentCreate
    ) -> VideoWithCommentResponse:
        channel = db.get(Channel, video_data.channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        author = db.get(User, channel.owner_id)
        if not author:
            raise HTTPException(status_code=404, detail="Channel owner not found")
        if author.is_deleted:
            raise HTTPException(
                status_code=410, detail="Channel owner has been deleted"
            )
        if author.is_banned:
            raise HTTPException(status_code=403, detail="Channel owner is banned")
        video = Video(
            title=video_data.title,
            description=video_data.description,
            uploaded_at=date.today(),
            channel_id=video_data.channel_id,
            is_active=video_data.is_active
            if video_data.is_active is not None
            else True,
            is_monetized=video_data.is_monetized
            if video_data.is_monetized is not None
            else False,
        )
        db.add(video)
        db.flush()
        comment = Comment(
            comment_text=video_data.initial_comment,
            user_id=author.id,
            video_id=video.id,
            commented_at=date.today(),
        )
        db.add(comment)
        db.commit()
        return VideoWithCommentResponse(
            video=video, comment_id=comment.id, comment_text=comment.comment_text
        )

from datetime import date

from sqlalchemy.orm import Session

from app.db.models import Channel, Comment, User, Video
from app.domain.errors import ForbiddenError, GoneError, NotFoundError
from app.infrastructure.mappers.orm_domain import comment_to_domain, video_to_domain
from app.repositories.video import VideoRepository
from app.presentation.schemas.schemas import (
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
            raise NotFoundError("Video not found")
        d_video = video_to_domain(video)
        return VideoResponse(
            id=d_video.id,
            title=d_video.title.value,
            description=d_video.description.value if d_video.description else None,
            channel_id=d_video.channel_id,
            uploaded_at=d_video.uploaded_at,
            is_active=d_video.is_active,
            is_monetized=d_video.is_monetized,
        )

    @staticmethod
    def create_video(db: Session, video_data: VideoCreate) -> VideoResponse:
        channel = db.get(Channel, video_data.channel_id)
        if not channel:
            raise NotFoundError("Channel not found")
        video = Video(
            title=video_data.title,
            description=video_data.description,
            uploaded_at=date.today(),
            channel_id=video_data.channel_id,
            is_active=video_data.is_active if video_data.is_active is not None else True,
            is_monetized=video_data.is_monetized if video_data.is_monetized is not None else False,
        )
        created = VideoRepository.create(db, video)
        d_video = video_to_domain(created)
        return VideoResponse(
            id=d_video.id,
            title=d_video.title.value,
            description=d_video.description.value if d_video.description else None,
            channel_id=d_video.channel_id,
            uploaded_at=d_video.uploaded_at,
            is_active=d_video.is_active,
            is_monetized=d_video.is_monetized,
        )

    @staticmethod
    def update_video(db: Session, video_id: int, video_data: VideoUpdate) -> VideoResponse:
        video = VideoRepository.get_by_id(db, video_id, for_update=True)
        if not video:
            raise NotFoundError("Video not found")
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
        d_video = video_to_domain(video)
        return VideoResponse(
            id=d_video.id,
            title=d_video.title.value,
            description=d_video.description.value if d_video.description else None,
            channel_id=d_video.channel_id,
            uploaded_at=d_video.uploaded_at,
            is_active=d_video.is_active,
            is_monetized=d_video.is_monetized,
        )

    @staticmethod
    def delete_video(db: Session, video_id: int) -> None:
        video = VideoRepository.get_by_id(db, video_id)
        if not video:
            raise NotFoundError("Video not found")
        VideoRepository.delete(db, video)

    @staticmethod
    def get_stats(db: Session, video_id: int) -> VideoStatsResponse:
        video = VideoRepository.get_by_id(db, video_id)
        if not video:
            raise NotFoundError("Video not found")
        total_views, likes, dislikes, total_comments = VideoRepository.get_stats(db, video_id)
        d_video = video_to_domain(video)
        return VideoStatsResponse(
            video_id=video_id,
            title=d_video.title.value,
            total_views=total_views or 0,
            likes=likes or 0,
            dislikes=dislikes or 0,
            total_comments=total_comments,
        )

    @staticmethod
    def get_comments(db: Session, video_id: int, page: int, limit: int) -> VideoCommentsResponse:
        video = VideoRepository.get_by_id(db, video_id)
        if not video:
            raise NotFoundError("Video not found")
        d_video = video_to_domain(video)
        skip = (page - 1) * limit
        total_count, comments = VideoRepository.get_comments(db, video_id, skip, limit)

        # NOTE: kept as-is for behavioral parity (could be optimized by mapping once per comment).
        return VideoCommentsResponse(
            video_id=video_id,
            title=d_video.title.value,
            comments=[
                CommentResponse(
                    id=comment_to_domain(comment).id,
                    comment_text=comment_to_domain(comment).comment_text.value,
                    commented_at=comment_to_domain(comment).commented_at,
                    user_id=comment_to_domain(comment).user_id,
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
            raise NotFoundError("Channel not found")
        author = db.get(User, channel.owner_id)
        if not author:
            raise NotFoundError("Channel owner not found")
        if author.is_deleted:
            raise GoneError("Channel owner has been deleted")
        if author.is_banned:
            raise ForbiddenError("Channel owner is banned")
        video = Video(
            title=video_data.title,
            description=video_data.description,
            uploaded_at=date.today(),
            channel_id=video_data.channel_id,
            is_active=video_data.is_active if video_data.is_active is not None else True,
            is_monetized=video_data.is_monetized if video_data.is_monetized is not None else False,
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
            video=video,
            comment_id=comment.id,
            comment_text=comment.comment_text,
        )

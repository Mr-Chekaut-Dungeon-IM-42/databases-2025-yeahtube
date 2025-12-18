from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.models import Video, View, Comment, User

class VideoRepository:
    @staticmethod
    def get_by_id(db: Session, video_id: int, for_update: bool = False):
        query = select(Video).where(Video.id == video_id)
        if for_update:
            query = query.with_for_update()
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def create(db: Session, video: Video):
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def delete(db: Session, video: Video):
        db.delete(video)
        db.commit()

    @staticmethod
    def get_stats(db: Session, video_id: int):
        stats_row = db.execute(
            select(
                func.count(View.user_id).label("total_views"),
                func.count(View.user_id).filter(View.reaction == "Liked").label("likes"),
                func.count(View.user_id).filter(View.reaction == "Disliked").label("dislikes")
            )
            .select_from(View)
            .where(View.video_id == video_id)
        ).one()
        total_comments = db.scalar(
            select(func.count(Comment.id)).where(Comment.video_id == video_id)
        ) or 0

        return (*stats_row, total_comments)

    @staticmethod
    def get_comments(db: Session, video_id: int, skip: int, limit: int):
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
        return total_count, comments

    @staticmethod
    def create_with_comment(db: Session, video: Video, comment: Comment):
        db.add(video)
        db.flush()
        db.add(comment)
        db.commit()
        return video, comment
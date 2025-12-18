from sqlalchemy import select, func, extract, desc
from sqlalchemy.orm import Session
from app.db.models import User, View, Video, Channel, Comment, Subscription, Report

class UserRepository:
    @staticmethod
    def get_all_active(db: Session):
        return db.execute(select(User).where(User.is_deleted == False)).scalars().all()

    @staticmethod
    def get_by_id(db: Session, user_id: int, for_update: bool = False):
        query = select(User).where(User.id == user_id)
        if for_update:
            query = query.with_for_update()
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def exists_by_username(db: Session, username: str, exclude_id: int = None):
        query = select(User).where(User.username == username)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        return db.execute(query).scalar_one_or_none() is not None

    @staticmethod
    def exists_by_email(db: Session, email: str, exclude_id: int = None):
        query = select(User).where(User.email == email)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        return db.execute(query).scalar_one_or_none() is not None

    @staticmethod
    def get_recommendations(db: Session, user_id: int, limit: int):
        user_channel_views = (
            select(Video.channel_id, func.count(View.user_id).label('channel_view_count'))
            .join(Video, View.video_id == Video.id)
            .where(View.user_id == user_id)
            .group_by(Video.channel_id).subquery()
        )
        subscriptions = select(Subscription.channel_id).where(Subscription.user_id == user_id).subquery()
        total_views = select(View.video_id, func.count(View.user_id).label('total_view_count')).group_by(View.video_id).subquery()

        query = (
            select(Video)
            .outerjoin(user_channel_views, Video.channel_id == user_channel_views.c.channel_id)
            .outerjoin(total_views, Video.id == total_views.c.video_id)
            .outerjoin(subscriptions, Video.channel_id == subscriptions.c.channel_id)
            .order_by(
                desc(func.coalesce(user_channel_views.c.channel_view_count, 0)),
                desc(subscriptions.c.channel_id.isnot(None)),
                desc(func.coalesce(total_views.c.total_view_count, 0))
            ).limit(limit)
        )
        return db.execute(query).scalars().all()

    @staticmethod
    def get_yearly_view_count(db: Session, user_id: int, year: int):
        return db.execute(
            select(func.count(View.video_id)).where(
                View.user_id == user_id,
                extract('year', View.watched_at) == year
            )
        ).scalar() or 0

    @staticmethod
    def get_favorite_creator(db: Session, user_id: int, year: int):
        return db.execute(
            select(Channel.name, func.count(View.video_id).label("view_count"))
            .join(Video, View.video_id == Video.id)
            .join(Channel, Video.channel_id == Channel.id)
            .where(View.user_id == user_id, extract('year', View.watched_at) == year)
            .group_by(Channel.id).order_by(desc("view_count")).limit(1)
        ).first()

    @staticmethod
    def get_avg_view_percentage(db: Session, user_id: int):
        return db.execute(
            select(func.avg(View.watched_percentage)).where(View.user_id == user_id)
        ).scalar()

    @staticmethod
    def get_yearly_reaction_counts(db: Session, user_id: int, year: int):
        comm_count = db.execute(
            select(func.count(Comment.id)).where(
                Comment.user_id == user_id, 
                extract('year', Comment.commented_at) == year
            )
        ).scalar() or 0
        
        react_count = db.execute(
            select(func.count(View.video_id)).where(
                View.user_id == user_id,
                extract('year', View.watched_at) == year,
                View.reaction.isnot(None)
            )
        ).scalar() or 0
        return comm_count, react_count

    @staticmethod
    def get_credibility_data(db: Session, user_id: int):
        return db.execute(
            select(
                User.id, User.username,
                func.count(Report.id).label("total_reports"),
                func.count(Report.id).filter(Report.is_resolved == True).label("approved_reports")
            )
            .outerjoin(Report, Report.reporter_id == User.id)
            .where(User.id == user_id).group_by(User.id, User.username)
        ).one_or_none()
from datetime import timedelta

from sqlalchemy import Float, Integer, func, select
from sqlalchemy.orm import Session

from app.db.models import Channel, ChannelStrike, Report, User, Video


class AdminRepository:
    @staticmethod
    def get_video_by_id(db: Session, video_id: int):
        return db.execute(
            select(Video).where(Video.id == video_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    @staticmethod
    def get_channel_by_id(db: Session, channel_id: int):
        return db.execute(
            select(Channel).where(Channel.id == channel_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_report_by_id(db: Session, report_id: int):
        return db.execute(
            select(Report).where(Report.id == report_id)
        ).scalar_one_or_none()

    @staticmethod
    def add_channel_strike(db: Session, channel_id: int, video_id: int | None = None):
        new_strike = ChannelStrike(
            channel_id=channel_id, duration=timedelta(days=7), video_id=video_id
        )
        db.add(new_strike)
        db.flush()
        return new_strike

    @staticmethod
    def get_channel_strikes_count(db: Session, channel_id: int) -> int:
        return (
            db.execute(
                select(func.count(ChannelStrike.id)).where(
                    ChannelStrike.channel_id == channel_id
                )
            ).scalar()
            or 0
        )

    @staticmethod
    def get_all_reports(
        db: Session, resolved: bool | None = None, skip: int = 0, limit: int = 50
    ):
        query = select(Report)

        if resolved is not None:
            query = query.where(Report.is_resolved == resolved)

        query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    @staticmethod
    def get_reports_with_details(
        db: Session, resolved: bool | None = None, skip: int = 0, limit: int = 50
    ):
        query = (
            select(Report, User.username, Video.title, Video.views)
            .join(User, Report.reporter_id == User.id)
            .join(Video, Report.video_id == Video.id)
        )

        if resolved is not None:
            query = query.where(Report.is_resolved == resolved)

        query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
        return db.execute(query).all()

    @staticmethod
    def get_problematic_users(
        db: Session, min_reports: int = 3, skip: int = 0, limit: int = 50
    ):
        query = (
            select(
                User.id,
                User.username,
                User.email,
                User.is_banned,
                func.count(Report.id).label("report_count"),
            )
            .join(Report, User.id == Report.reporter_id)
            .group_by(User.id, User.username, User.email, User.is_banned)
            .having(func.count(Report.id) >= min_reports)
            .order_by(func.count(Report.id).desc())
            .offset(skip)
            .limit(limit)
        )
        return db.execute(query).all()

    @staticmethod
    def get_channels_with_reports_analytics(
        db: Session, min_reports: int = 1, limit: int = 20
    ):
        strikes_subquery = (
            select(
                ChannelStrike.channel_id,
                func.count(ChannelStrike.id).label("strikes_count"),
            )
            .group_by(ChannelStrike.channel_id)
            .subquery()
        )

        query = (
            select(
                Channel.id.label("channel_id"),
                Channel.name.label("channel_name"),
                func.coalesce(strikes_subquery.c.strikes_count, 0).label("strikes"),
                User.username.label("owner_username"),
                func.count(Report.id).label("total_reports"),
                func.count(func.distinct(Video.id)).label("reported_videos_count"),
                func.count(func.distinct(Report.reporter_id)).label("unique_reporters"),
                (
                    func.cast(func.sum(func.cast(Report.is_resolved, Integer)), Float)
                    / func.count(Report.id)
                    * 100
                ).label("resolved_percentage"),
            )
            .join(Video, Channel.id == Video.channel_id)
            .join(Report, Video.id == Report.video_id)
            .join(User, Channel.owner_id == User.id)
            .outerjoin(strikes_subquery, Channel.id == strikes_subquery.c.channel_id)
            .group_by(
                Channel.id,
                Channel.name,
                strikes_subquery.c.strikes_count,
                User.username,
            )
            .having(func.count(Report.id) >= min_reports)
            .order_by(func.count(Report.id).desc())
            .limit(limit)
        )
        return db.execute(query).all()

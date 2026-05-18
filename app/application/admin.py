from sqlalchemy.orm import Session

from app.domain.errors import NotFoundError, ValidationError
from app.infrastructure.mappers.orm_domain import channel_to_domain, user_to_domain, video_to_domain
from app.repositories.admin import AdminRepository
from app.presentation.schemas.schemas import (
    ChannelAnalyticsListResponse,
    ChannelAnalyticsResponse,
    ChannelInfo,
    ChannelStrikeResponse,
    DetailedReportResponse,
    DetailedReportsListResponse,
    ProblematicUsersListResponse,
    ProblematicUserResponse,
    ReportResolveResponse,
    ReportResponse,
    ReportStats,
    ReportsListResponse,
    ReporterInfo,
    UserBanResponse,
    VideoDeactivateResponse,
    VideoDemonetizeResponse,
    VideoInfo,
)


class AdminService:
    @staticmethod
    def deactivate_video(db: Session, video_id: int) -> VideoDeactivateResponse:
        video = AdminRepository.get_video_by_id(db, video_id)

        if not video:
            raise NotFoundError("Video not found")

        if not video.is_active:
            raise ValidationError("Video is already inactive")

        video.is_active = False
        db.commit()
        db.refresh(video)
        d_video = video_to_domain(video)

        return VideoDeactivateResponse(
            message="Video deactivated successfully",
            video_id=d_video.id,
            title=d_video.title.value,
            is_active=d_video.is_active,
        )

    @staticmethod
    def demonetize_video(db: Session, video_id: int) -> VideoDemonetizeResponse:
        video = AdminRepository.get_video_by_id(db, video_id)

        if not video:
            raise NotFoundError("Video not found")

        if not video.is_monetized:
            raise ValidationError("Video is already not monetized")

        video.is_monetized = False
        db.commit()
        db.refresh(video)
        d_video = video_to_domain(video)

        return VideoDemonetizeResponse(
            message="Video demonetized successfully",
            video_id=d_video.id,
            title=d_video.title.value,
            is_monetized=d_video.is_monetized,
        )

    @staticmethod
    def ban_user(db: Session, user_id: int) -> UserBanResponse:
        user = AdminRepository.get_user_by_id(db, user_id)

        if not user:
            raise NotFoundError("User not found")

        if user.is_banned:
            raise ValidationError("User is already banned")

        user.is_banned = True
        db.commit()
        db.refresh(user)
        d_user = user_to_domain(user)

        return UserBanResponse(
            message="User banned successfully",
            user_id=d_user.id,
            username=d_user.username.value,
            is_banned=d_user.is_banned,
        )

    @staticmethod
    def add_channel_strike(db: Session, channel_id: int) -> ChannelStrikeResponse:
        channel = AdminRepository.get_channel_by_id(db, channel_id)

        if not channel:
            raise NotFoundError("Channel not found")

        AdminRepository.add_channel_strike(db, channel.id, video_id=None)
        db.commit()

        strikes_count = AdminRepository.get_channel_strikes_count(db, channel_id)
        d_channel = channel_to_domain(channel)

        penalty_message = ""
        if strikes_count >= 3:
            penalty_message = (
                " Channel has reached 3 strikes and may face additional penalties."
            )

        return ChannelStrikeResponse(
            message=f"Strike added to channel successfully.{penalty_message}",
            channel_id=d_channel.id,
            channel_name=d_channel.name.value,
            strikes=strikes_count,
        )

    @staticmethod
    def get_all_reports(
        db: Session, resolved: bool | None = None, skip: int = 0, limit: int = 50
    ) -> ReportsListResponse:
        reports = AdminRepository.get_all_reports(db, resolved, skip, limit)

        return ReportsListResponse(
            reports=[
                ReportResponse(
                    id=report.id,
                    reason=report.reason,
                    created_at=report.created_at,
                    is_resolved=report.is_resolved,
                    reporter_id=report.reporter_id,
                    video_id=report.video_id,
                )
                for report in reports
            ],
            count=len(reports),
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def resolve_report(db: Session, report_id: int) -> ReportResolveResponse:
        report = AdminRepository.get_report_by_id(db, report_id)

        if not report:
            raise NotFoundError("Report not found")

        if report.is_resolved:
            raise ValidationError("Report is already resolved")

        report.is_resolved = True
        db.commit()
        db.refresh(report)

        return ReportResolveResponse(
            message="Report resolved successfully",
            report_id=report.id,
            is_resolved=report.is_resolved,
            video_id=report.video_id,
        )

    @staticmethod
    def get_reports_with_details(
        db: Session, resolved: bool | None = None, skip: int = 0, limit: int = 50
    ) -> DetailedReportsListResponse:
        results = AdminRepository.get_reports_with_details(db, resolved, skip, limit)

        return DetailedReportsListResponse(
            reports=[
                DetailedReportResponse(
                    id=report.id,
                    reason=report.reason,
                    created_at=report.created_at,
                    is_resolved=report.is_resolved,
                    reporter=ReporterInfo(id=report.reporter_id, username=username),
                    video=VideoInfo(id=report.video_id, title=title),
                )
                for report, username, title in results
            ],
            count=len(results),
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def get_problematic_users(
        db: Session, min_reports: int = 3, skip: int = 0, limit: int = 50
    ) -> ProblematicUsersListResponse:
        results = AdminRepository.get_problematic_users(db, min_reports, skip, limit)

        return ProblematicUsersListResponse(
            users=[
                ProblematicUserResponse(
                    id=user_id,
                    username=username,
                    email=email,
                    is_banned=is_banned,
            reports_created=reports_count,
                )
                for user_id, username, email, is_banned, reports_count in results
            ],
            count=len(results),
        min_reports_threshold=min_reports,
        )

    @staticmethod
    def get_channels_with_reports_analytics(
        db: Session, min_reports: int = 1, limit: int = 20
    ) -> ChannelAnalyticsListResponse:
        results = AdminRepository.get_channels_with_reports_analytics(db, min_reports, limit)

        analytics: list[ChannelAnalyticsResponse] = []
        for (
            channel_id,
            channel_name,
            strikes,
            owner_username,
            total_reports,
            reported_videos_count,
            unique_reporters,
            resolved_percentage,
        ) in results:
            risk_level = "LOW"
            if (total_reports or 0) >= 10 or (strikes or 0) >= 3:
                risk_level = "HIGH"
            elif (total_reports or 0) >= 3 or (strikes or 0) >= 1:
                risk_level = "MEDIUM"

            analytics.append(
                ChannelAnalyticsResponse(
                    channel=ChannelInfo(
                        id=channel_id,
                        name=channel_name,
                        strikes=int(strikes or 0),
                        owner_username=owner_username,
                    ),
                    report_stats=ReportStats(
                        total_reports=int(total_reports or 0),
                        reported_videos_count=int(reported_videos_count or 0),
                        unique_reporters=int(unique_reporters or 0),
                        resolved_percentage=float(resolved_percentage or 0.0),
                    ),
                    risk_level=risk_level,
                )
            )

        return ChannelAnalyticsListResponse(
            analytics=analytics,
            count=len(analytics),
            min_reports_threshold=min_reports,
        )

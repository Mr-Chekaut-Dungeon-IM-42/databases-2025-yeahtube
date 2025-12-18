from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.admin import AdminRepository
from app.schemas.schemas import (
    ChannelAnalyticsListResponse,
    ChannelAnalyticsResponse,
    ChannelStrikeResponse,
    DetailedReportResponse,
    DetailedReportsListResponse,
    ProblematicUserResponse,
    ProblematicUsersListResponse,
    ReporterInfo,
    ReportResolveResponse,
    ReportResponse,
    ReportsListResponse,
    ReportStats,
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        if not video.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video is already inactive",
            )

        video.is_active = False
        db.commit()
        db.refresh(video)

        return VideoDeactivateResponse(
            message="Video deactivated successfully",
            video_id=video.id,
            title=video.title,
            is_active=video.is_active,
        )

    @staticmethod
    def demonetize_video(db: Session, video_id: int) -> VideoDemonetizeResponse:
        video = AdminRepository.get_video_by_id(db, video_id)

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        if not video.is_monetized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video is already not monetized",
            )

        video.is_monetized = False
        db.commit()
        db.refresh(video)

        return VideoDemonetizeResponse(
            message="Video demonetized successfully",
            video_id=video.id,
            title=video.title,
            is_monetized=video.is_monetized,
        )

    @staticmethod
    def ban_user(db: Session, user_id: int) -> UserBanResponse:
        user = AdminRepository.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is already banned"
            )

        user.is_banned = True
        db.commit()
        db.refresh(user)

        return UserBanResponse(
            message="User banned successfully",
            user_id=user.id,
            username=user.username,
            is_banned=user.is_banned,
        )

    @staticmethod
    def add_channel_strike(db: Session, channel_id: int) -> ChannelStrikeResponse:
        channel = AdminRepository.get_channel_by_id(db, channel_id)

        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
            )

        AdminRepository.add_channel_strike(db, channel.id, video_id=None)
        db.commit()

        strikes_count = AdminRepository.get_channel_strikes_count(db, channel_id)

        penalty_message = ""
        if strikes_count >= 3:
            penalty_message = (
                " Channel has reached 3 strikes and may face additional penalties."
            )

        return ChannelStrikeResponse(
            message=f"Strike added to channel successfully.{penalty_message}",
            channel_id=channel.id,
            channel_name=channel.name,
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
            )

        if report.is_resolved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report is already resolved",
            )

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
                    reports_created=report_count,
                )
                for user_id, username, email, is_banned, report_count in results
            ],
            count=len(results),
            min_reports_threshold=min_reports,
        )

    @staticmethod
    def get_channels_with_reports_analytics(
        db: Session, min_reports: int = 1, limit: int = 20
    ) -> ChannelAnalyticsListResponse:
        results = AdminRepository.get_channels_with_reports_analytics(
            db, min_reports, limit
        )

        return ChannelAnalyticsListResponse(
            analytics=[
                ChannelAnalyticsResponse(
                    channel=ChannelInfo(
                        id=channel_id,
                        name=channel_name,
                        strikes=strikes,
                        owner_username=owner_username,
                    ),
                    report_stats=ReportStats(
                        total_reports=total_reports,
                        reported_videos_count=reported_videos_count,
                        unique_reporters=unique_reporters,
                        resolved_percentage=round(resolved_percentage, 2)
                        if resolved_percentage
                        else 0.0,
                    ),
                    risk_level=(
                        "HIGH"
                        if total_reports >= 10 or strikes >= 2
                        else "MEDIUM"
                        if total_reports >= 5 or strikes >= 1
                        else "LOW"
                    ),
                )
                for (
                    channel_id,
                    channel_name,
                    strikes,
                    owner_username,
                    total_reports,
                    reported_videos_count,
                    unique_reporters,
                    resolved_percentage,
                ) in results
            ],
            count=len(results),
            min_reports_threshold=min_reports,
        )

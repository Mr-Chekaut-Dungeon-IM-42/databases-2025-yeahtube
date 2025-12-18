from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Float, Integer, func, select

from app.db.models import Channel, ChannelStrike, Report, User, Video
from app.db.session import DBDep
from app.dependencies import require_admin
from app.schemas.schemas import (
    ChannelAnalyticsListResponse,
    ChannelAnalyticsResponse,
    ChannelInfo,
    ChannelStrikeResponse,
    DetailedReportResponse,
    DetailedReportsListResponse,
    ProblematicUsersListResponse,
    ProblematicUserResponse,
    ReportResolveResponse,
    ReportStats,
    ReportsListResponse,
    ReporterInfo,
    UserBanResponse,
    VideoDeactivateResponse,
    VideoDemonetizeResponse,
    VideoInfo,
    ReportResponse,
)

router = APIRouter(
    tags=["admin"], prefix="/admin", dependencies=[Depends(require_admin)]
)


@router.patch("/video/{video_id}/deactivate", response_model=VideoDeactivateResponse)
async def deactivate_video(video_id: int, db: DBDep) -> VideoDeactivateResponse:
    video = db.execute(select(Video).where(Video.id == video_id)).scalar_one_or_none()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    if not video.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Video is already inactive"
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


@router.patch("/video/{video_id}/demonetize", response_model=VideoDemonetizeResponse)
async def demonetize_video(video_id: int, db: DBDep) -> VideoDemonetizeResponse:
    video = db.execute(select(Video).where(Video.id == video_id)).scalar_one_or_none()

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


@router.post("/user/{user_id}/ban", response_model=UserBanResponse)
async def ban_user(user_id: int, db: DBDep) -> UserBanResponse:
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

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


@router.post("/channel/{channel_id}/strike", response_model=ChannelStrikeResponse)
async def add_channel_strike(channel_id: int, db: DBDep) -> ChannelStrikeResponse:
    channel = db.execute(
        select(Channel).where(Channel.id == channel_id)
    ).scalar_one_or_none()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )

    new_strike = ChannelStrike(
        channel_id=channel.id, duration=timedelta(days=7), video_id=None
    )
    db.add(new_strike)
    db.commit()

    strikes_count = db.execute(
        select(func.count(ChannelStrike.id)).where(
            ChannelStrike.channel_id == channel_id
        )
    ).scalar()

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


@router.get("/reports", response_model=ReportsListResponse)
async def get_all_reports(
    db: DBDep, resolved: bool | None = None, skip: int = 0, limit: int = 50
) -> ReportsListResponse:
    query = select(Report)

    if resolved is not None:
        query = query.where(Report.is_resolved == resolved)

    query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)

    reports = db.execute(query).scalars().all()

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


@router.patch("/report/{report_id}/resolve", response_model=ReportResolveResponse)
async def resolve_report(report_id: int, db: DBDep) -> ReportResolveResponse:
    report = db.execute(
        select(Report).where(Report.id == report_id)
    ).scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    if report.is_resolved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Report is already resolved"
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


@router.get("/reports/detailed", response_model=DetailedReportsListResponse)
async def get_reports_with_details(
    db: DBDep, resolved: bool | None = None, skip: int = 0, limit: int = 50
) -> DetailedReportsListResponse:
    query = (
        select(Report, User.username, Video.title)
        .join(User, Report.reporter_id == User.id)
        .join(Video, Report.video_id == Video.id)
    )

    if resolved is not None:
        query = query.where(Report.is_resolved == resolved)

    query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)

    results = db.execute(query).all()

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


@router.get("/users/problematic", response_model=ProblematicUsersListResponse)
async def get_problematic_users(
    db: DBDep, min_reports: int = 3, skip: int = 0, limit: int = 50
) -> ProblematicUsersListResponse:
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

    results = db.execute(query).all()

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


@router.get(
    "/analytics/channels-reports-stats", response_model=ChannelAnalyticsListResponse
)
async def get_channels_with_reports_analytics(
    db: DBDep, min_reports: int = 1, limit: int = 20
) -> ChannelAnalyticsListResponse:
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
            Channel.id, Channel.name, strikes_subquery.c.strikes_count, User.username
        )
        .having(func.count(Report.id) >= min_reports)
        .order_by(func.count(Report.id).desc())
        .limit(limit)
    )

    results = db.execute(query).all()

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

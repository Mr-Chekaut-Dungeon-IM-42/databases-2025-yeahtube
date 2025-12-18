from fastapi import APIRouter, Depends
from app.db.session import DBDep
from app.dependencies import require_admin
from app.services.admin import AdminService
from app.schemas.schemas import (
    ChannelAnalyticsListResponse,
    ChannelStrikeResponse,
    DetailedReportsListResponse,
    ProblematicUsersListResponse,
    ReportResolveResponse,
    ReportsListResponse,
    UserBanResponse,
    VideoDeactivateResponse,
    VideoDemonetizeResponse,
)

router = APIRouter(
    tags=["admin"], prefix="/admin", dependencies=[Depends(require_admin)]
)


@router.patch("/video/{video_id}/deactivate", response_model=VideoDeactivateResponse)
async def deactivate_video(video_id: int, db: DBDep) -> VideoDeactivateResponse:
    return AdminService.deactivate_video(db, video_id)


@router.patch("/video/{video_id}/demonetize", response_model=VideoDemonetizeResponse)
async def demonetize_video(video_id: int, db: DBDep) -> VideoDemonetizeResponse:
    return AdminService.demonetize_video(db, video_id)


@router.post("/user/{user_id}/ban", response_model=UserBanResponse)
async def ban_user(user_id: int, db: DBDep) -> UserBanResponse:
    return AdminService.ban_user(db, user_id)


@router.post("/channel/{channel_id}/strike", response_model=ChannelStrikeResponse)
async def add_channel_strike(channel_id: int, db: DBDep) -> ChannelStrikeResponse:
    return AdminService.add_channel_strike(db, channel_id)


@router.get("/reports", response_model=ReportsListResponse)
async def get_all_reports(
    db: DBDep, resolved: bool | None = None, skip: int = 0, limit: int = 50
) -> ReportsListResponse:
    return AdminService.get_all_reports(db, resolved, skip, limit)


@router.patch("/report/{report_id}/resolve", response_model=ReportResolveResponse)
async def resolve_report(report_id: int, db: DBDep) -> ReportResolveResponse:
    return AdminService.resolve_report(db, report_id)


@router.get("/reports/detailed", response_model=DetailedReportsListResponse)
async def get_reports_with_details(
    db: DBDep, resolved: bool | None = None, skip: int = 0, limit: int = 50
) -> DetailedReportsListResponse:
    return AdminService.get_reports_with_details(db, resolved, skip, limit)


@router.get("/users/problematic", response_model=ProblematicUsersListResponse)
async def get_problematic_users(
    db: DBDep, min_reports: int = 3, skip: int = 0, limit: int = 50
) -> ProblematicUsersListResponse:
    return AdminService.get_problematic_users(db, min_reports, skip, limit)


@router.get(
    "/analytics/channels-reports-stats", response_model=ChannelAnalyticsListResponse
)
async def get_channels_with_reports_analytics(
    db: DBDep, min_reports: int = 1, limit: int = 20
) -> ChannelAnalyticsListResponse:
    return AdminService.get_channels_with_reports_analytics(db, min_reports, limit)

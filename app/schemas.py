from pydantic import BaseModel, Field

class VideoResponse(BaseModel):
    id: int
    title: str
    is_active: bool
    is_monetized: bool


class UserResponse(BaseModel):
    id: int
    username: str
    is_banned: bool


class ChannelResponse(BaseModel):
    id: int
    name: str
    strikes: int


class ReportResponse(BaseModel):
    id: int
    reason: str
    created_at: str
    is_resolved: bool
    reporter_id: int
    video_id: int

class ReporterInfo(BaseModel):
    id: int
    username: str


class VideoInfo(BaseModel):
    id: int
    title: str


class DetailedReportResponse(BaseModel):
    id: int
    reason: str
    created_at: str
    is_resolved: bool
    reporter: ReporterInfo
    video: VideoInfo


class ProblematicUserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_banned: bool
    reports_created: int


class ChannelInfo(BaseModel):
    id: int
    name: str
    strikes: int
    owner_username: str


class ReportStats(BaseModel):
    total_reports: int
    reported_videos_count: int
    unique_reporters: int
    resolved_percentage: float


class ChannelAnalyticsResponse(BaseModel):
    channel: ChannelInfo
    report_stats: ReportStats
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, or HIGH")


class VideoDeactivateResponse(BaseModel):
    message: str
    video_id: int
    title: str
    is_active: bool


class VideoDemonetizeResponse(BaseModel):
    message: str
    video_id: int
    title: str
    is_monetized: bool


class UserBanResponse(BaseModel):
    message: str
    user_id: int
    username: str
    is_banned: bool


class ChannelStrikeResponse(BaseModel):
    message: str
    channel_id: int
    channel_name: str
    strikes: int


class ReportResolveResponse(BaseModel):
    message: str
    report_id: int
    is_resolved: bool
    video_id: int


class ReportsListResponse(BaseModel):
    reports: list[ReportResponse]
    count: int
    skip: int
    limit: int


class DetailedReportsListResponse(BaseModel):
    reports: list[DetailedReportResponse]
    count: int
    skip: int
    limit: int


class ProblematicUsersListResponse(BaseModel):
    users: list[ProblematicUserResponse]
    count: int
    min_reports_threshold: int


class ChannelAnalyticsListResponse(BaseModel):
    analytics: list[ChannelAnalyticsResponse]
    count: int
    min_reports_threshold: int
    
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VideoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    channel_id: int
    uploaded_at: date
    is_active: bool
    is_monetized: bool
    
    model_config = ConfigDict(from_attributes=True)

class VideoCreate(BaseModel):
    title: str = Field(..., max_length=128)
    description: str | None = Field(None, max_length=256)
    channel_id: int
    is_active: bool | None = True
    is_monetized: bool | None = False


class VideoUpdate(BaseModel):
    title: str | None = Field(None, max_length=128)
    description: str | None = Field(None, max_length=256)
    is_active: bool | None = None
    is_monetized: bool | None = None

class VideoWithCommentCreate(BaseModel):
    title: str = Field(..., max_length=128)
    description: str | None = Field(None, max_length=256)
    channel_id: int
    initial_comment: str = Field(..., min_length=1, max_length=2048)
    is_active: bool | None = True
    is_monetized: bool | None = False

class VideoWithCommentResponse(BaseModel):
    video: VideoResponse
    comment_id: int
    comment_text: str

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


class VideoInfo(BaseModel):
    id: int
    title: str

class VideoStatsResponse(BaseModel):
    video_id: int
    title: str
    total_views: int
    likes: int
    dislikes: int
    total_comments: int

class CommentResponse(BaseModel):
    id: int
    comment_text: str
    commented_at: date
    user_id: int
    username: str


class VideoCommentsResponse(BaseModel):
    video_id: int
    title: str
    comments: list[CommentResponse]
    total_comments: int
    page: int
    limit: int
    total_pages: int

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    is_moderator: bool = False


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    is_moderator: bool | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_banned: bool

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_moderator: bool
    is_banned: bool
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class UserDetailedResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: date
    is_moderator: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)

class UserCredibilityResponse(BaseModel):
    
    user_id: int
    username: str
    total_reports: int
    approved_reports: int
    credibility_score: float

    model_config = ConfigDict(from_attributes=True)

class UserBanResponse(BaseModel):
    message: str
    user_id: int
    username: str
    is_banned: bool


class ProblematicUserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_banned: bool
    reports_created: int


class ProblematicUsersListResponse(BaseModel):
    users: list[ProblematicUserResponse]
    count: int
    min_reports_threshold: int


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: str = Field(max_length=64)
    password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    username: str
    is_moderator: bool


class ChannelResponse(BaseModel):
    id: int
    name: str
    strikes: int


class ChannelStrikeResponse(BaseModel):
    message: str
    channel_id: int
    channel_name: str
    strikes: int


class ChannelInfo(BaseModel):
    id: int
    name: str
    strikes: int
    owner_username: str


class ChannelAnalyticsResponse(BaseModel):
    channel: ChannelInfo
    report_stats: "ReportStats"
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, or HIGH")


class ChannelAnalyticsListResponse(BaseModel):
    analytics: list[ChannelAnalyticsResponse]
    count: int
    min_reports_threshold: int


class ReportResponse(BaseModel):
    id: int
    reason: str
    created_at: date
    is_resolved: bool
    reporter_id: int
    video_id: int


class ReporterInfo(BaseModel):
    id: int
    username: str


class DetailedReportResponse(BaseModel):
    id: int
    reason: str
    created_at: date
    is_resolved: bool
    reporter: ReporterInfo
    video: VideoInfo


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


class ReportStats(BaseModel):
    total_reports: int
    reported_videos_count: int
    unique_reporters: int
    resolved_percentage: float

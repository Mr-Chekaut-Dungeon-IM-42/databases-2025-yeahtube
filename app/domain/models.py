from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from app.domain.value_objects import BoundedText, Email, WatchedPercentage


@dataclass(frozen=True, slots=True)
class UserD:
    id: int
    username: BoundedText
    email: Email
    created_at: date
    is_moderator: bool
    is_deleted: bool
    is_banned: bool


@dataclass(frozen=True, slots=True)
class ChannelD:
    id: int
    name: BoundedText
    created_at: date
    owner_id: int


@dataclass(frozen=True, slots=True)
class VideoD:
    id: int
    title: BoundedText
    description: Optional[BoundedText]
    uploaded_at: date
    is_active: bool
    is_monetized: bool
    channel_id: int


@dataclass(frozen=True, slots=True)
class CommentD:
    id: int
    comment_text: BoundedText
    commented_at: date
    user_id: int
    video_id: int


@dataclass(frozen=True, slots=True)
class PlaylistD:
    id: int
    name: BoundedText
    created_at: date
    author_id: int


@dataclass(frozen=True, slots=True)
class SubscriptionD:
    user_id: int
    channel_id: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class PaidSubscriptionD:
    id: int
    active_since: datetime
    active_to: Optional[datetime]
    tier: str
    sub_user_id: int
    sub_channel_id: int


@dataclass(frozen=True, slots=True)
class ChannelStrikeD:
    id: int
    issued_at: datetime
    duration: timedelta
    video_id: int | None
    channel_id: int


@dataclass(frozen=True, slots=True)
class ViewD:
    id: int
    watched_at: date
    watch_duration: timedelta | None
    watched_percentage: WatchedPercentage
    reaction: str | None
    user_id: int
    video_id: int

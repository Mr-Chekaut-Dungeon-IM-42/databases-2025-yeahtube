from __future__ import annotations

from app.db import models as orm
from app.domain.models import (
    ChannelD,
    ChannelStrikeD,
    CommentD,
    PaidSubscriptionD,
    PlaylistD,
    SubscriptionD,
    UserD,
    VideoD,
    ViewD,
)
from app.domain.value_objects import BoundedText, Email, WatchedPercentage

def user_to_domain(u: orm.User) -> UserD:
    return UserD(
        id=u.id,
        username=BoundedText(u.username, 3, 32),
        email=Email(u.email),
        created_at=u.created_at,
        is_moderator=bool(u.is_moderator),
        is_deleted=bool(u.is_deleted),
        is_banned=bool(u.is_banned),
    )


def user_to_orm(d: UserD, *, hashed_password: str) -> orm.User:
    return orm.User(
        id=d.id,
        username=d.username.value,
        email=d.email.value,
        hashed_password=hashed_password,
        created_at=d.created_at,
        is_moderator=d.is_moderator,
        is_deleted=d.is_deleted,
        is_banned=d.is_banned,
    )


def channel_to_domain(c: orm.Channel) -> ChannelD:
    return ChannelD(
        id=c.id,
        name=BoundedText(c.name, 1, 32),
        created_at=c.created_at,
        owner_id=c.owner_id,
    )


def channel_to_orm(d: ChannelD) -> orm.Channel:
    return orm.Channel(
        id=d.id,
        name=d.name.value,
        created_at=d.created_at,
        owner_id=d.owner_id,
    )


def video_to_domain(v: orm.Video) -> VideoD:
    return VideoD(
        id=v.id,
        title=BoundedText(v.title, 1, 128),
        description=(BoundedText(v.description, 0, 256) if v.description is not None else None),
        uploaded_at=v.uploaded_at,
        is_active=bool(v.is_active),
        is_monetized=bool(v.is_monetized),
        channel_id=v.channel_id,
    )


def video_to_orm(d: VideoD) -> orm.Video:
    return orm.Video(
        id=d.id,
        title=d.title.value,
        description=d.description.value if d.description else None,
        uploaded_at=d.uploaded_at,
        is_active=d.is_active,
        is_monetized=d.is_monetized,
        channel_id=d.channel_id,
    )


def comment_to_domain(c: orm.Comment) -> CommentD:
    return CommentD(
        id=c.id,
        comment_text=BoundedText(c.comment_text, 1, 2048),
        commented_at=c.commented_at,
        user_id=c.user_id,
        video_id=c.video_id,
    )


def comment_to_orm(d: CommentD) -> orm.Comment:
    return orm.Comment(
        id=d.id,
        comment_text=d.comment_text.value,
        commented_at=d.commented_at,
        user_id=d.user_id,
        video_id=d.video_id,
    )


def playlist_to_domain(p: orm.Playlist) -> PlaylistD:
    return PlaylistD(
        id=p.id,
        name=BoundedText(p.name, 1, 64),
        created_at=p.created_at,
        author_id=p.author_id,
    )


def playlist_to_orm(d: PlaylistD) -> orm.Playlist:
    return orm.Playlist(
        id=d.id,
        name=d.name.value,
        created_at=d.created_at,
        author_id=d.author_id,
    )


def subscription_to_domain(s: orm.Subscription) -> SubscriptionD:
    return SubscriptionD(user_id=s.user_id, channel_id=s.channel_id, is_active=bool(s.is_active))


def subscription_to_orm(d: SubscriptionD) -> orm.Subscription:
    return orm.Subscription(user_id=d.user_id, channel_id=d.channel_id, is_active=d.is_active)


def paid_subscription_to_domain(p: orm.PaidSubscription) -> PaidSubscriptionD:
    return PaidSubscriptionD(
        id=p.id,
        active_since=p.active_since,
        active_to=p.active_to,
        tier=p.tier.name if hasattr(p.tier, "name") else str(p.tier),
        sub_user_id=p.sub_user_id,
        sub_channel_id=p.sub_channel_id,
    )


def channel_strike_to_domain(s: orm.ChannelStrike) -> ChannelStrikeD:
    return ChannelStrikeD(
        id=s.id,
        issued_at=s.issued_at,
        duration=s.duration,
        video_id=s.video_id,
        channel_id=s.channel_id,
    )


def view_to_domain(v: orm.View) -> ViewD:
    return ViewD(
        id=v.id,
        watched_at=v.watched_at,
        watch_duration=v.watch_duration,
        watched_percentage=WatchedPercentage(v.watched_percentage),
        reaction=v.reaction,
        user_id=v.user_id,
        video_id=v.video_id,
    )

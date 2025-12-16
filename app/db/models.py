from __future__ import annotations

import enum
from datetime import datetime, timedelta

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Interval,
    MetaData,
    String,
    Text,
    func,
    text,
    true,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

naming_convention: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[str] = mapped_column(Date, nullable=False)
    is_moderator: Mapped[bool] = mapped_column(default=False, nullable=False)

    channels: Mapped[list["Channel"]] = relationship(
        "Channel", back_populates="owner", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist", back_populates="author", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )
    views: Mapped[list["View"]] = relationship(
        "View", back_populates="user", cascade="all, delete-orphan"
    )


class ChannelStrike(Base):
    __tablename__ = "channel_strikes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    duration: Mapped[timedelta] = mapped_column(Interval)
    video_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("videos.id"), nullable=True
    )
    channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("channels.id", ondelete="CASCADE")
    )

    video: Mapped[Video | None] = relationship(
        "Video", back_populates="channel_strikes"
    )
    channel: Mapped[Channel] = relationship("Channel", back_populates="channel_strikes")


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[str] = mapped_column(Date, nullable=False)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner: Mapped[User] = relationship("User", back_populates="channels")
    videos: Mapped[list["Video"]] = relationship(
        "Video", back_populates="channel", cascade="all, delete-orphan"
    )
    subscribers: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="channel", cascade="all, delete-orphan"
    )
    strikes: Mapped[list["ChannelStrike"]] = relationship(
        "ChannelStrike", back_populates="channel", cascade="all, delete-orphan"
    )


class Video(Base):
    __tablename__ = "videos"
    __table_args__ = (
        CheckConstraint("length(title) <= 128", name="ck_videos_title_length"),
        CheckConstraint(
            "length(description) <= 256", name="ck_videos_description_length"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    channel: Mapped[Channel] = relationship("Channel", back_populates="videos")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="video", cascade="all, delete-orphan"
    )
    playlist_entries: Mapped[list["PlaylistVideo"]] = relationship(
        "PlaylistVideo", back_populates="video", cascade="all, delete-orphan"
    )
    views: Mapped[list["View"]] = relationship(
        "View", back_populates="video", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint("length(comment_text) <= 2048", name="ck_comments_text_length"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    commented_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="comments")
    video: Mapped[Video] = relationship("Video", back_populates="comments")


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    author: Mapped[User] = relationship("User", back_populates="playlists")
    videos: Mapped[list["PlaylistVideo"]] = relationship(
        "PlaylistVideo", back_populates="playlist", cascade="all, delete-orphan"
    )


class PlaylistVideo(Base):
    __tablename__ = "playlist_video"

    playlist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True
    )

    playlist: Mapped[Playlist] = relationship("Playlist", back_populates="videos")
    video: Mapped[Video] = relationship("Video", back_populates="playlist_entries")


class Subscription(Base):
    __tablename__ = "subscription"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    paid_subs: Mapped[list[PaidSubscription]] = relationship(
        "PaidSubscription", back_populates="subscription"
    )

    user: Mapped[User] = relationship("User", back_populates="subscriptions")
    channel: Mapped[Channel] = relationship("Channel", back_populates="subscribers")


class PaidSubTier(enum.Enum):
    BRONZE = 4.99
    SILVER = 7.49
    GOLD = 9.99
    DIAMOND = 17.49


class PaidSubscription(Base):
    __tablename__ = "paid_subscriptions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sub_user_id", "sub_channel_id"],
            ["subscription.user_id", "subscription.channel_id"],
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    active_since: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    active_to: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), nullable=True
    )
    tier: Mapped[PaidSubTier] = mapped_column(Enum(PaidSubTier))

    sub_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sub_channel_id: Mapped[int] = mapped_column(Integer, nullable=False)

    sub: Mapped[Subscription] = relationship("Subscription", back_populates="paid_subs")


class View(Base):
    __tablename__ = "views"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True
    )
    watched_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )

    user: Mapped[User] = relationship("User", back_populates="views")
    video: Mapped[Video] = relationship("Video", back_populates="views")

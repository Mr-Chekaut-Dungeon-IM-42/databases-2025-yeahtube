from __future__ import annotations

from typing import Literal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
    text,
    Float,
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
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(Date, nullable=False)
    is_moderator: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)

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
    reports_created: Mapped[list["Report"]] = relationship(
        "Report", back_populates="reporter", cascade="all, delete-orphan"
    )


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[str] = mapped_column(Date, nullable=False)
    strikes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_monetized: Mapped[bool] = mapped_column(default=False, nullable=False)
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
    reports: Mapped[list["Report"]] = relationship(
        "Report", back_populates="video", cascade="all, delete-orphan"
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

    user: Mapped[User] = relationship("User", back_populates="subscriptions")
    channel: Mapped[Channel] = relationship("Channel", back_populates="subscribers")


class View(Base):
    __tablename__ = "views"

    __table_args__ = (
        CheckConstraint("watched_percentage >= 0.0 AND watched_percentage <= 1.0", name="ck_views_watched_amount"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True
    )
    watched_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    watched_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    reaction: Mapped[Literal["Liked", "Disliked"]| None] = mapped_column(String, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="views")
    video: Mapped[Video] = relationship("Video", back_populates="views")


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        CheckConstraint("length(reason) <= 512", name="ck_reports_reason_length"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    is_resolved: Mapped[bool] = mapped_column(default=False, nullable=False)
    reporter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )

    reporter: Mapped[User] = relationship("User", back_populates="reports_created")
    video: Mapped[Video] = relationship("Video", back_populates="reports")

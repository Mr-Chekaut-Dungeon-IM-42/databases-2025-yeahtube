from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
    false,
    func,
    text,
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


class Moderator(Base):
    __tablename__ = "moderators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(
        Date, nullable=False, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped[User] = relationship("User", back_populates="moderators")


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

    user: Mapped[User] = relationship("User", back_populates="subscriptions")
    channel: Mapped[Channel] = relationship("Channel", back_populates="subscribers")


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

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import User, Playlist

class PlaylistRepository:
    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.get(User, user_id)

    @staticmethod
    def create(db: Session, name: str, author_id: int):
        playlist = Playlist(name=name, author_id=author_id)
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        return playlist

    @staticmethod
    def get_all_by_user(db: Session, user_id: int):
        return db.execute(select(Playlist).where(Playlist.author_id == user_id)).scalars().all()

    @staticmethod
    def get_by_id(db: Session, playlist_id: int, author_id: int):
        return db.execute(
            select(Playlist).where(Playlist.id == playlist_id, Playlist.author_id == author_id)
        ).scalar_one_or_none()

    @staticmethod
    def update(db: Session, playlist, name: str):
        playlist.name = name
        db.commit()
        db.refresh(playlist)
        return playlist

    @staticmethod
    def delete(db: Session, playlist):
        db.delete(playlist)
        db.commit()
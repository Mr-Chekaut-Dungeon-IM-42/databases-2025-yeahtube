from sqlalchemy.orm import Session

from app.domain.errors import NotFoundError
from app.infrastructure.mappers.orm_domain import playlist_to_domain
from app.repositories.playlist import PlaylistRepository


class PlaylistService:
    @staticmethod
    def create_playlist(db: Session, user_id: int, name: str):
        if not PlaylistRepository.get_user(db, user_id):
            raise NotFoundError("User not found")
        playlist = PlaylistRepository.create(db, name, user_id)
        d_playlist = playlist_to_domain(playlist)
        return {
            "id": d_playlist.id,
            "name": d_playlist.name.value,
            "created_at": d_playlist.created_at,
            "author_id": d_playlist.author_id,
        }

    @staticmethod
    def get_user_playlists(db: Session, user_id: int):
        if not PlaylistRepository.get_user(db, user_id):
            raise NotFoundError("User not found")
        playlists = PlaylistRepository.get_all_by_user(db, user_id)
        return [
            {
                "id": (d := playlist_to_domain(p)).id,
                "name": d.name.value,
                "created_at": d.created_at,
                "author_id": d.author_id,
            }
            for p in playlists
        ]

    @staticmethod
    def get_playlist(db: Session, user_id: int, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user_id)
        if not playlist:
            raise NotFoundError("Playlist not found")
        d_playlist = playlist_to_domain(playlist)
        return {
            "id": d_playlist.id,
            "name": d_playlist.name.value,
            "created_at": d_playlist.created_at,
            "author_id": d_playlist.author_id,
        }

    @staticmethod
    def update_playlist(db: Session, user_id: int, playlist_id: int, name: str):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user_id)
        if not playlist:
            raise NotFoundError("Playlist not found")
        playlist = PlaylistRepository.update(db, playlist, name)
        d_playlist = playlist_to_domain(playlist)
        return {
            "id": d_playlist.id,
            "name": d_playlist.name.value,
            "created_at": d_playlist.created_at,
            "author_id": d_playlist.author_id,
        }

    @staticmethod
    def delete_playlist(db: Session, user_id: int, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user_id)
        if not playlist:
            raise NotFoundError("Playlist not found")
        PlaylistRepository.delete(db, playlist)

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.playlist import PlaylistRepository

class PlaylistService:
    @staticmethod
    def create_playlist(db: Session, user_id: int, name: str):
        if not PlaylistRepository.get_user(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")
        playlist = PlaylistRepository.create(db, name, user_id)
        return {
            "id": playlist.id,
            "name": playlist.name,
            "created_at": playlist.created_at,
            "author_id": playlist.author_id
        }

    @staticmethod
    def get_user_playlists(db: Session, user_id: int):
        if not PlaylistRepository.get_user(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")
        playlists = PlaylistRepository.get_all_by_user(db, user_id)
        return [
            {
                "id": p.id,
                "name": p.name,
                "created_at": p.created_at,
                "author_id": p.author_id
            }
            for p in playlists
        ]

    @staticmethod
    def get_playlist(db: Session, user_id: int, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return {
            "id": playlist.id,
            "name": playlist.name,
            "created_at": playlist.created_at,
            "author_id": playlist.author_id
        }

    @staticmethod
    def update_playlist(db: Session, user_id: int, playlist_id: int, name: str):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        playlist = PlaylistRepository.update(db, playlist, name)
        return {
            "id": playlist.id,
            "name": playlist.name,
            "created_at": playlist.created_at,
            "author_id": playlist.author_id
        }

    @staticmethod
    def delete_playlist(db: Session, user_id: int, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        PlaylistRepository.delete(db, playlist)
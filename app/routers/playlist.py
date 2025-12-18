from fastapi import APIRouter, Body, status

from app.db.session import DBDep
from app.services.playlist import PlaylistService

router = APIRouter(tags=["playlist"], prefix="/playlist")


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_playlist(user_id: int, db: DBDep, name: str = Body(..., embed=True)):
    return PlaylistService.create_playlist(db, user_id, name)


@router.get("/{user_id}")
async def read_user_playlists(user_id: int, db: DBDep):
    return PlaylistService.get_user_playlists(db, user_id)


@router.get("/{user_id}/{playlist_id}")
async def read_playlist(user_id: int, playlist_id: int, db: DBDep):
    return PlaylistService.get_playlist(db, user_id, playlist_id)


@router.put("/{user_id}/{playlist_id}")
async def update_playlist(
    user_id: int, playlist_id: int, db: DBDep, name: str = Body(..., embed=True)
):
    return PlaylistService.update_playlist(db, user_id, playlist_id, name)


@router.delete("/{user_id}/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(user_id: int, playlist_id: int, db: DBDep):
    PlaylistService.delete_playlist(db, user_id, playlist_id)
    return None

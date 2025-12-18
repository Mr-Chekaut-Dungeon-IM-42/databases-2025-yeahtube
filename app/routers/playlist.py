from fastapi import APIRouter, HTTPException, status, Body
from sqlalchemy import select

from app.db.models import User, Playlist
from app.db.session import DBDep

router = APIRouter(tags=["playlist"], prefix="/playlist")

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_playlist(
    user_id: int, 
    db: DBDep, 
    name: str = Body(..., embed=True)
):
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    new_playlist = Playlist(
        name=name,
        author_id=user_id
    )
    
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    
    return {
        "id": new_playlist.id,
        "name": new_playlist.name,
        "created_at": new_playlist.created_at,
        "author_id": new_playlist.author_id
    }

@router.get("/{user_id}")
async def read_user_playlists(user_id: int, db: DBDep):
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
        
    query = select(Playlist).where(Playlist.author_id == user_id)
    playlists = db.execute(query).scalars().all()
    
    return [
        {
            "id": p.id, 
            "name": p.name, 
            "created_at": p.created_at, 
            "author_id": p.author_id
        } 
        for p in playlists
    ]


@router.get("/{user_id}/{playlist_id}")
async def read_playlist(user_id: int, playlist_id: int, db: DBDep):
    query = select(Playlist).where(
        Playlist.id == playlist_id, 
        Playlist.author_id == user_id
    )
    playlist = db.execute(query).scalar_one_or_none()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
        
    return {
        "id": playlist.id,
        "name": playlist.name,
        "created_at": playlist.created_at,
        "author_id": playlist.author_id
    }


@router.put("/{user_id}/{playlist_id}")
async def update_playlist(
    user_id: int, 
    playlist_id: int, 
    db: DBDep,
    name: str = Body(..., embed=True)
):
    query = select(Playlist).where(
        Playlist.id == playlist_id, 
        Playlist.author_id == user_id
    )
    playlist = db.execute(query).scalar_one_or_none()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist.name = name
    db.commit()
    db.refresh(playlist)
    
    return {
        "id": playlist.id,
        "name": playlist.name,
        "created_at": playlist.created_at,
        "author_id": playlist.author_id
    }


@router.delete("/{user_id}/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(user_id: int, playlist_id: int, db: DBDep):
    query = select(Playlist).where(
        Playlist.id == playlist_id, 
        Playlist.author_id == user_id
    )
    playlist = db.execute(query).scalar_one_or_none()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    db.delete(playlist)
    db.commit()
    
    return None
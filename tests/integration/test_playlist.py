from datetime import date
from app.db.models import User, Playlist

def test_create_playlist(client, db):
    playlist_data = {"name": "My Favorites"}
    response = client.post("/playlist/99999", json=playlist_data)
    assert response.status_code == 404

    user = User(
        username="create_tester",
        email="test@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False
    )
    db.add(user)
    db.commit()

    response = client.post(f"/playlist/{user.id}", json=playlist_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["name"] == "My Favorites"
    assert data["author_id"] == user.id
    
    db_playlist = db.get(Playlist, data["id"])
    assert db_playlist is not None
    assert db_playlist.name == "My Favorites"


def test_get_user_playlists(client, db):
    response = client.get("/playlist/99999")
    assert response.status_code == 404

    user = User(
        username="get_tester",
        email="test@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False
    )
    db.add(user)
    db.commit()

    response = client.get(f"/playlist/{user.id}")
    assert response.status_code == 200
    assert response.json() == []

    p1 = Playlist(name="Gym", author_id=user.id, created_at=date.today())
    p2 = Playlist(name="Relax", author_id=user.id, created_at=date.today())
    db.add_all([p1, p2])
    db.commit()

    response = client.get(f"/playlist/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [p["name"] for p in data]
    assert "Gym" in names
    assert "Relax" in names


def test_get_single_playlist(client, db):
    user = User(
        username="single_tester", 
        email="test@example.com", 
        hashed_password="fake_hash",
        created_at=date.today(), 
        is_moderator=False
    )
    db.add(user)
    db.commit()

    playlist = Playlist(name="Rock", author_id=user.id, created_at=date.today())
    db.add(playlist)
    db.commit()

    response = client.get(f"/playlist/{user.id}/99999")
    assert response.status_code == 404

    response = client.get(f"/playlist/{user.id}/{playlist.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == playlist.id
    assert data["name"] == "Rock"
    assert data["author_id"] == user.id


def test_update_playlist(client, db):
    user = User(
        username="update_tester", 
        email="test@example.com", 
        hashed_password="fake_hash",
        created_at=date.today(), 
        is_moderator=False
    )
    db.add(user)
    db.commit()

    playlist = Playlist(name="Old Name", author_id=user.id, created_at=date.today())
    db.add(playlist)
    db.commit()

    update_data = {"name": "New Name"}
    response = client.put(f"/playlist/{user.id}/99999", json=update_data)
    assert response.status_code == 404

    response = client.put(f"/playlist/{user.id}/{playlist.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"

    db.refresh(playlist)
    assert playlist.name == "New Name"


def test_delete_playlist(client, db):
    user = User(
        username="delete_tester", 
        email="test@example.com", 
        hashed_password="fake_hash",
        created_at=date.today(), 
        is_moderator=False
    )
    db.add(user)
    db.commit()

    playlist = Playlist(name="To Delete", author_id=user.id, created_at=date.today())
    db.add(playlist)
    db.commit()

    response = client.delete(f"/playlist/{user.id}/99999")
    assert response.status_code == 404

    response = client.delete(f"/playlist/{user.id}/{playlist.id}")
    assert response.status_code == 204

    deleted_playlist = db.get(Playlist, playlist.id)
    assert deleted_playlist is None

    response = client.get(f"/playlist/{user.id}/{playlist.id}")
    assert response.status_code == 404
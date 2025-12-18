from datetime import date

from app.db.models import Video, Channel, User, Comment, View


def test_get_video(client, db):
    response = client.get("/video/99999")
    assert response.status_code == 404
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    
    channel = Channel(name="Test Channel", owner_id=user.id, created_at=date.today())
    db.add(channel)
    db.commit()
    
    video = Video(
        title="Test Video",
        description="Test Description",
        channel_id=channel.id,
        uploaded_at=date.today(),
        is_active=True,
        is_monetized=False,
    )
    db.add(video)
    db.commit()
    
    response = client.get(f"/video/{video.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == video.id
    assert data["title"] == "Test Video"
    assert data["channel_id"] == channel.id


def test_create_video(client, db):
    video_data = {
        "title": "New Video",
        "description": "New Description",
        "channel_id": 99999,
    }
    response = client.post("/video/", json=video_data)
    assert response.status_code == 404
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    
    channel = Channel(name="Test Channel", owner_id=user.id, created_at=date.today())
    db.add(channel)
    db.commit()
    
    video_data = {
        "title": "New Video",
        "description": "New Description",
        "channel_id": channel.id,
        "is_active": True,
        "is_monetized": True,
    }
    response = client.post("/video/", json=video_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Video"
    assert data["is_active"] is True
    assert data["is_monetized"] is True
    
    video_data_defaults = {
        "title": "Video with Defaults",
        "channel_id": channel.id,
    }
    response = client.post("/video/", json=video_data_defaults)
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is True
    assert data["is_monetized"] is False


def test_update_video(client, db):
    response = client.patch("/video/99999", json={"title": "Updated"})
    assert response.status_code == 404
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    
    channel = Channel(name="Test Channel", owner_id=user.id, created_at=date.today())
    db.add(channel)
    db.commit()
    
    video = Video(
        title="Original Title",
        description="Original Description",
        channel_id=channel.id,
        uploaded_at=date.today(),
        is_active=True,
        is_monetized=False,
    )
    db.add(video)
    db.commit()
    
    response = client.patch(f"/video/{video.id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original Description"
    
    response = client.patch(f"/video/{video.id}", json={
        "title": "Final Title",
        "is_monetized": True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Final Title"
    assert data["is_monetized"] is True


def test_delete_video(client, db):
    response = client.delete("/video/99999")
    assert response.status_code == 404
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    
    channel = Channel(name="Test Channel", owner_id=user.id, created_at=date.today())
    db.add(channel)
    db.commit()
    
    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    db.add(video)
    db.commit()
    video_id = video.id
    
    response = client.delete(f"/video/{video_id}")
    assert response.status_code == 204
    assert db.get(Video, video_id) is None
    
    response = client.delete(f"/video/{video_id}")
    assert response.status_code == 404


def test_get_video_stats(client, db):
    response = client.get("/video/99999/stats")
    assert response.status_code == 404
    
    user1 = User(username="user1", email="user1@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    user2 = User(username="user2", email="user2@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    user3 = User(username="user3", email="user3@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    db.add_all([user1, user2, user3])
    db.commit()
    
    channel = Channel(name="Test Channel", owner_id=user1.id, created_at=date.today())
    db.add(channel)
    db.commit()
    
    video = Video(title="Test Video", channel_id=channel.id, uploaded_at=date.today())
    db.add(video)
    db.commit()
    
    response = client.get(f"/video/{video.id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["video_id"] == video.id
    assert data["total_views"] == 0
    assert data["likes"] == 0
    assert data["dislikes"] == 0
    assert data["total_comments"] == 0
    
    view1 = View(user_id=user1.id, video_id=video.id, reaction="Liked")
    view2 = View(user_id=user2.id, video_id=video.id, reaction="Liked")
    view3 = View(user_id=user3.id, video_id=video.id, reaction="Disliked")
    comment1 = Comment(comment_text="Great!", user_id=user1.id, video_id=video.id, commented_at=date.today())
    comment2 = Comment(comment_text="Nice!", user_id=user2.id, video_id=video.id, commented_at=date.today())
    comment3 = Comment(comment_text="Cool!", user_id=user3.id, video_id=video.id, commented_at=date.today())
    db.add_all([view1, view2, view3, comment1, comment2, comment3])
    db.commit()
    
    response = client.get(f"/video/{video.id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_views"] == 3
    assert data["likes"] == 2
    assert data["dislikes"] == 1
    assert data["total_comments"] == 3


def test_get_video_comments(client, db):
    response = client.get("/video/99999/comments")
    assert response.status_code == 404
    
    user = User(username="user1", email="user1@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    db.add(user)
    db.commit()
    
    channel = Channel(name="Test Channel", owner_id=user.id, created_at=date.today())
    db.add(channel)
    db.commit()
    
    video = Video(title="Test Video", channel_id=channel.id, uploaded_at=date.today())
    db.add(video)
    db.commit()
    
    response = client.get(f"/video/{video.id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["total_comments"] == 0
    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["comments"]) == 0
    
    for i in range(15):
        comment = Comment(comment_text=f"Comment {i}", user_id=user.id, video_id=video.id, commented_at=date.today())
        db.add(comment)
    db.commit()
    
    response = client.get(f"/video/{video.id}/comments?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_comments"] == 15
    assert data["page"] == 1
    assert data["total_pages"] == 2
    assert len(data["comments"]) == 10
    
    response = client.get(f"/video/{video.id}/comments?page=2&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["comments"]) == 5
    
    response = client.get(f"/video/{video.id}/comments?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["total_pages"] == 3
    assert len(data["comments"]) == 5
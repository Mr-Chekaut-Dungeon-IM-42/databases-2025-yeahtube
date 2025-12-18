from datetime import date

from app.db.models import User, Report, Channel, View, Video, Subscription

def test_get_users(client, db):
    user1 = User(
        username="alice",
        email="alice@example.com",
        hashed_password="fake_hash",
        created_at=date(2024, 1, 1),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    user2 = User(
        username="bob",
        email="bob@example.com",
        hashed_password="fake_hash",
        created_at=date(2024, 1, 2),
        is_moderator=True,
        is_deleted=False,
        is_banned=False,
    )
    deleted_user = User(
        username="deleted",
        email="deleted@example.com",
        hashed_password="fake_hash",
        created_at=date(2024, 1, 3),
        is_moderator=False,
        is_deleted=True,
        is_banned=False,
    )
    db.add_all([user1, user2, deleted_user])
    db.commit()
    
    response = client.get("/user/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 2
    usernames = [u["username"] for u in data["users"]]
    assert "alice" in usernames
    assert "bob" in usernames
    assert "deleted" not in usernames

def test_update_user(client, db):
    user = User(
        username="originaluser",
        email="original@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()

    response = client.patch(f"/user/{user.id}", json={
        "username": "updateduser"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "original@example.com"

    response = client.patch(f"/user/{user.id}", json={
        "username": "finaluser",
        "email": "final@example.com",
        "is_moderator": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "finaluser"
    assert data["email"] == "final@example.com"
    assert data["is_moderator"] == True

    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(other_user)
    db.commit()
    
    response = client.patch(f"/user/{user.id}", json={
        "username": "otheruser"
    })
    assert response.status_code == 400

    response = client.patch("/user/99999", json={
        "username": "newname"
    })
    assert response.status_code == 404

    user.is_deleted = True
    db.commit()
    
    response = client.patch(f"/user/{user.id}", json={
        "username": "nope"
    })
    assert response.status_code == 410

def test_concurrent_user_update(client, db):
    user = User(
        username="concurrentuser",
        email="concurrent@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()

    response1 = client.patch(f"/user/{user.id}", json={"username": "user1"})
    response2 = client.patch(f"/user/{user.id}", json={"username": "user2"})

    assert response1.status_code == 200
    assert response2.status_code == 200

    db.refresh(user)
    assert user.username == "user2"

def test_soft_delete_user(client, db):
    user = User(
        username="deleteuser",
        email="delete@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    user_id = user.id

    response = client.delete(f"/user/{user_id}")
    assert response.status_code == 204

    db.refresh(user)
    assert user.is_deleted == True

    response = client.delete(f"/user/{user_id}")
    assert response.status_code == 410

    response = client.patch(f"/user/{user_id}", json={
        "username": "newname"
    })
    assert response.status_code == 410

    response = client.delete("/user/99999")
    assert response.status_code == 404

def test_recommendations(client, db):
    """Test that recommendations respect priority order: watched channels > subscriptions > total views"""

    response = client.get("/user/99999/recommendations")
    assert response.status_code == 404

    deleted_user = User(
        username="deleteduser",
        email="deleted@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=True,
        is_banned=False,
    )
    db.add(deleted_user)
    db.commit()
    
    response = client.get(f"/user/{deleted_user.id}/recommendations")
    assert response.status_code == 410

    viewer = User(username="viewer", email="viewer@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    creator1 = User(username="creator1", email="creator1@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    creator2 = User(username="creator2", email="creator2@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    creator3 = User(username="creator3", email="creator3@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    db.add_all([viewer, creator1, creator2, creator3])
    db.commit()

    channel1 = Channel(name="Most Watched Channel", created_at=date.today(), owner_id=creator1.id)
    channel2 = Channel(name="Subscribed Channel", created_at=date.today(), owner_id=creator2.id)
    channel3 = Channel(name="Popular Channel", created_at=date.today(), owner_id=creator3.id)
    db.add_all([channel1, channel2, channel3])
    db.commit()

    video1_ch1 = Video(title="Watched Video 1", channel_id=channel1.id, uploaded_at=date.today())
    video2_ch1 = Video(title="Watched Video 2", channel_id=channel1.id, uploaded_at=date.today())
    video1_ch2 = Video(title="Subscribed Video", channel_id=channel2.id, uploaded_at=date.today())
    video1_ch3 = Video(title="Popular Video", channel_id=channel3.id, uploaded_at=date.today())
    db.add_all([video1_ch1, video2_ch1, video1_ch2, video1_ch3])
    db.commit()

    view1 = View(user_id=viewer.id, video_id=video1_ch1.id, watched_at=date.today())
    view2 = View(user_id=viewer.id, video_id=video2_ch1.id, watched_at=date.today())
    db.add_all([view1, view2])
    db.commit()

    subscription = Subscription(user_id=viewer.id, channel_id=channel2.id)
    db.add(subscription)
    db.commit()

    other_user1 = User(username="other1", email="other1@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    other_user2 = User(username="other2", email="other2@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    other_user3 = User(username="other3", email="other3@example.com", hashed_password="fake_hash", created_at=date.today(), is_moderator=False, is_deleted=False, is_banned=False)
    db.add_all([other_user1, other_user2, other_user3])
    db.commit()
    
    view_ch1_v2_1 = View(user_id=other_user1.id, video_id=video2_ch1.id, watched_at=date.today())
    view_ch1_v2_2 = View(user_id=other_user2.id, video_id=video2_ch1.id, watched_at=date.today())
    view_ch1_v1_1 = View(user_id=other_user3.id, video_id=video1_ch1.id, watched_at=date.today())
    
    view_popular1 = View(user_id=other_user1.id, video_id=video1_ch3.id, watched_at=date.today())
    view_popular2 = View(user_id=other_user2.id, video_id=video1_ch3.id, watched_at=date.today())
    view_popular3 = View(user_id=other_user3.id, video_id=video1_ch3.id, watched_at=date.today())
    
    db.add_all([view_ch1_v2_1, view_ch1_v2_2, view_ch1_v1_1, view_popular1, view_popular2, view_popular3])
    db.commit()

    response = client.get(f"/user/{viewer.id}/recommendations?limit=10")
    
    assert response.status_code == 200
    videos = response.json()["videos"]
    
    video_ids = [v["id"] for v in videos]
    
    assert video_ids[0] == video2_ch1.id
    assert video_ids[1] == video1_ch1.id
    assert video_ids[2] == video1_ch2.id
    assert video_ids[3] == video1_ch3.id

def test_user_credibility(client, db):
    reporter = User(
        username="reporter",
        email="reporter@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    creator = User(
        username="creator",
        email="creator@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add_all([reporter, creator])
    db.commit()

    channel = Channel(name="Test Channel", created_at=date.today(), owner=creator)
    db.add(channel)
    db.commit()
    
    video = Video(title="Test Video", channel=channel, uploaded_at=date.today())
    db.add(video)
    db.commit()

    for i in range(10):
        is_resolved = i < 7
        report = Report(
            reason=f"Test report {i}",
            created_at=date.today(),
            is_resolved=is_resolved,
            reporter=reporter,
            video=video,
        )
        db.add(report)
    db.commit()

    response = client.get(f"/user/{reporter.id}/credibility")
    assert response.status_code == 200
    
    data = response.json()
    assert data["user_id"] == reporter.id
    assert data["username"] == "reporter"
    assert data["total_reports"] == 10
    assert data["approved_reports"] == 7
    assert data["credibility_score"] == 70.0

    response = client.get(f"/user/{creator.id}/credibility")
    assert response.status_code == 200
    
    data = response.json()
    assert data["user_id"] == creator.id
    assert data["username"] == "creator"
    assert data["total_reports"] == 0
    assert data["approved_reports"] == 0
    assert data["credibility_score"] == 0.0

    response = client.get("/user/99999/stats/credibility")
    assert response.status_code == 404

    reporter.is_deleted = True
    db.commit()
    
    response = client.get(f"/user/{reporter.id}/credibility")
    assert response.status_code == 410
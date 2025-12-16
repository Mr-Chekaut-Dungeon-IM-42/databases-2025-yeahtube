from datetime import date

from app.db.models import User, Channel, View, Video, Subscription
from sqlalchemy import select


def test_get_users_with_data(client, db):
    """Test getting users with existing data"""
    user1 = User(
        username="alice",
        email="alice@example.com",
        created_at=date(2024, 1, 1),
        is_moderator=False
    )
    user2 = User(
        username="bob",
        email="bob@example.com",
        created_at=date(2024, 1, 2),
        is_moderator=True
    )
    db.add_all([user1, user2])
    db.commit()
    
    response = client.get("/user/test")
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 2
    
    usernames = [u["username"] for u in data["users"]]
    assert "alice" in usernames
    assert "bob" in usernames

def test_create_user(client, db):
    response = client.post("/user/", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "is_moderator": False
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["is_moderator"] == False
    assert "id" in data
    user_id = data["id"]

    user = db.execute(select(User).where(User.id == user_id)).scalar_one()
    assert user.username == "newuser"
    assert user.email == "newuser@example.com"

    response = client.post("/user/", json={
        "username": "newuser",
        "email": "different@example.com",
        "is_moderator": False
    })
    assert response.status_code == 400

    response = client.post("/user/", json={
        "username": "differentuser",
        "email": "newuser@example.com",
        "is_moderator": False
    })
    assert response.status_code == 400

def test_recommendations(client, db):
    """Test that recommendations respect priority order: watched channels > subscriptions > total views"""

    viewer = User(username="viewer", email="viewer@example.com", created_at=date.today(), is_moderator=False)
    creator1 = User(username="creator1", email="creator1@example.com", created_at=date.today(), is_moderator=False)
    creator2 = User(username="creator2", email="creator2@example.com", created_at=date.today(), is_moderator=False)
    creator3 = User(username="creator3", email="creator3@example.com", created_at=date.today(), is_moderator=False)
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

    other_user1 = User(username="other1", email="other1@example.com", created_at=date.today(), is_moderator=False)
    other_user2 = User(username="other2", email="other2@example.com", created_at=date.today(), is_moderator=False)
    other_user3 = User(username="other3", email="other3@example.com", created_at=date.today(), is_moderator=False)
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

    response = client.get(f"/user/recommendations/{viewer.id}?limit=10")
    
    assert response.status_code == 200
    videos = response.json()["videos"]
    
    video_ids = [v["id"] for v in videos]
    
    assert video_ids[0] == video2_ch1.id  # Priority 1: most watched channel by the user, more views (3 total)
    assert video_ids[1] == video1_ch1.id  # Priority 1: most watched channel by the user, fewer views (2 total)
    assert video_ids[2] == video1_ch2.id  # Priority 2: subscribed channel
    assert video_ids[3] == video1_ch3.id  # Priority 3: popular video (3 total views)
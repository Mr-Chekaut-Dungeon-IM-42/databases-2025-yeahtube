from datetime import date

from app.db.models import User


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
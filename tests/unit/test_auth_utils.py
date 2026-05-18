from datetime import timedelta

from app.utils.auth import create_access_token, decode_access_token


def test_create_and_decode_access_token_roundtrip():
    token = create_access_token({"user_id": 123, "username": "alice", "is_moderator": False})
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["user_id"] == 123
    assert payload["username"] == "alice"
    assert payload["is_moderator"] is False
    assert "exp" in payload


def test_decode_access_token_invalid_returns_none():
    assert decode_access_token("this.is.not.a.jwt") is None


def test_access_token_expired_returns_none():
    token = create_access_token({"user_id": 1}, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None



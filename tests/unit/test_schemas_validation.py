import pytest
from pydantic import ValidationError

from app.presentation.schemas.schemas import UserUpdate, VideoWithCommentCreate


def test_user_update_validates_email():
    with pytest.raises(ValidationError):
        UserUpdate(email="not-an-email")

    model = UserUpdate(email="valid@example.com")
    assert model.email == "valid@example.com"


def test_video_with_comment_create_comment_constraints():
    with pytest.raises(ValidationError):
        VideoWithCommentCreate(title="t", channel_id=1, initial_comment="")

    model = VideoWithCommentCreate(title="video", channel_id=1, initial_comment="ok")
    assert model.initial_comment == "ok"

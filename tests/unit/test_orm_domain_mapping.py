from datetime import date

from app.db import models as orm
from app.infrastructure.mappers.orm_domain import user_to_domain, video_to_domain


def test_user_to_domain_maps_and_validates():
    u = orm.User(
        id=1,
        username="user123",
        email="user@example.com",
        hashed_password="x",
        created_at=date(2024, 1, 1),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    d = user_to_domain(u)
    assert d.id == 1
    assert d.username.value == "user123"
    assert d.email.value == "user@example.com"


def test_video_to_domain_maps_optional_description():
    v = orm.Video(
        id=10,
        title="t",
        description=None,
        uploaded_at=date(2024, 1, 1),
        is_active=True,
        is_monetized=False,
        channel_id=5,
    )
    d = video_to_domain(v)
    assert d.description is None

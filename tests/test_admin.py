from datetime import date, timedelta
import pytest

from app.db.models import Channel, ChannelStrike, Report, User, Video
from app.utils.auth import create_access_token


@pytest.fixture
def admin_user(db):
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=True,
        is_deleted=False,
        is_banned=False,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user):
    token = create_access_token(data={"user_id": admin_user.id})
    return token


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def regular_user(db):
    user = User(
        username="regular_user",
        email="regular@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user_token(regular_user):
    token = create_access_token(data={"user_id": regular_user.id})
    return token


@pytest.fixture
def regular_user_headers(regular_user_token):
    return {"Authorization": f"Bearer {regular_user_token}"}


def test_admin_endpoints_require_authentication(client, db):
    endpoints = [
        ("patch", "/admin/video/1/deactivate"),
        ("patch", "/admin/video/1/demonetize"),
        ("post", "/admin/user/1/ban"),
        ("post", "/admin/channel/1/strike"),
        ("get", "/admin/reports"),
        ("patch", "/admin/report/1/resolve"),
        ("get", "/admin/reports/detailed"),
        ("get", "/admin/users/problematic"),
        ("get", "/admin/analytics/channels-reports-stats"),
    ]

    for method, endpoint in endpoints:
        if method == "get":
            response = client.get(endpoint)
        elif method == "post":
            response = client.post(endpoint)
        elif method == "patch":
            response = client.patch(endpoint)

        assert response.status_code == 401, (
            f"Expected 401 for {method.upper()} {endpoint}, got {response.status_code}"
        )
        assert (
            "not authenticated" in response.json()["detail"].lower()
            or "credentials" in response.json()["detail"].lower()
        )


def test_admin_endpoints_require_admin_privileges(client, db, regular_user_headers):
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(owner)
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    db.add(video)
    db.commit()

    endpoints = [
        ("patch", f"/admin/video/{video.id}/deactivate"),
        ("patch", f"/admin/video/{video.id}/demonetize"),
        ("post", f"/admin/user/{owner.id}/ban"),
        ("post", f"/admin/channel/{channel.id}/strike"),
        ("get", "/admin/reports"),
        ("get", "/admin/reports/detailed"),
        ("get", "/admin/users/problematic"),
        ("get", "/admin/analytics/channels-reports-stats"),
    ]

    for method, endpoint in endpoints:
        if method == "get":
            response = client.get(endpoint, headers=regular_user_headers)
        elif method == "post":
            response = client.post(endpoint, headers=regular_user_headers)
        elif method == "patch":
            response = client.patch(endpoint, headers=regular_user_headers)

        assert response.status_code == 403, (
            f"Expected 403 for {method.upper()} {endpoint}, got {response.status_code}"
        )
        assert (
            "admin" in response.json()["detail"].lower()
            or "forbidden" in response.json()["detail"].lower()
        )


def test_admin_endpoints_with_invalid_token(client):
    invalid_headers = {"Authorization": "Bearer invalid_token_12345"}

    endpoints = [
        ("get", "/admin/reports"),
        ("get", "/admin/users/problematic"),
    ]

    for method, endpoint in endpoints:
        if method == "get":
            response = client.get(endpoint, headers=invalid_headers)

        assert response.status_code == 401, (
            f"Expected 401 for {method.upper()} {endpoint} with invalid token"
        )


def test_deactivate_video(client, db, admin_headers):
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(owner)
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
        is_active=True,
        is_monetized=True,
    )
    db.add(video)
    db.commit()

    response = client.patch(
        f"/admin/video/{video.id}/deactivate", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Video deactivated successfully"
    assert data["video_id"] == video.id
    assert data["is_active"] is False

    response = client.patch(
        f"/admin/video/{video.id}/deactivate", headers=admin_headers
    )
    assert response.status_code == 400
    assert "already inactive" in response.json()["detail"]

    response = client.patch("/admin/video/99999/deactivate", headers=admin_headers)
    assert response.status_code == 404


def test_demonetize_video(client, db, admin_headers):
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(owner)
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
        is_active=True,
        is_monetized=True,
    )
    db.add(video)
    db.commit()

    response = client.patch(
        f"/admin/video/{video.id}/demonetize", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Video demonetized successfully"
    assert data["video_id"] == video.id
    assert data["is_monetized"] is False

    response = client.patch(
        f"/admin/video/{video.id}/demonetize", headers=admin_headers
    )
    assert response.status_code == 400
    assert "already not monetized" in response.json()["detail"]

    response = client.patch("/admin/video/99999/demonetize", headers=admin_headers)
    assert response.status_code == 404


def test_ban_user(client, db, admin_headers):
    user = User(
        username="normaluser",
        email="user@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(user)
    db.commit()

    response = client.post(f"/admin/user/{user.id}/ban", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User banned successfully"
    assert data["user_id"] == user.id
    assert data["username"] == "normaluser"
    assert data["is_banned"] is True

    response = client.post(f"/admin/user/{user.id}/ban", headers=admin_headers)
    assert response.status_code == 400
    assert "already banned" in response.json()["detail"]

    response = client.post("/admin/user/99999/ban", headers=admin_headers)
    assert response.status_code == 404


def test_add_channel_strike(client, db, admin_headers):
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add(owner)
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    response = client.post(f"/admin/channel/{channel.id}/strike", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["strikes"] == 1
    assert data["channel_id"] == channel.id
    assert "Strike added" in data["message"]

    response = client.post(f"/admin/channel/{channel.id}/strike", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["strikes"] == 2

    response = client.post(f"/admin/channel/{channel.id}/strike", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["strikes"] == 3
    assert "3 strikes" in data["message"]
    assert "penalties" in data["message"]

    response = client.post("/admin/channel/99999/strike", headers=admin_headers)
    assert response.status_code == 404


def test_get_all_reports(client, db, admin_headers):
    reporter = User(
        username="reporter",
        email="reporter@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add_all([reporter, owner])
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    db.add(video)
    db.commit()

    report1 = Report(
        reason="Inappropriate content",
        reporter_id=reporter.id,
        video_id=video.id,
        created_at=date.today(),
        is_resolved=False,
    )
    report2 = Report(
        reason="Spam",
        reporter_id=reporter.id,
        video_id=video.id,
        created_at=date.today(),
        is_resolved=True,
    )
    db.add_all([report1, report2])
    db.commit()

    response = client.get("/admin/reports", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["reports"]) == 2

    response = client.get("/admin/reports?resolved=false", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["reports"][0]["is_resolved"] is False

    response = client.get("/admin/reports?resolved=true", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["reports"][0]["is_resolved"] is True

    response = client.get("/admin/reports?skip=1&limit=1", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["skip"] == 1
    assert data["limit"] == 1


def test_resolve_report(client, db, admin_headers):
    reporter = User(
        username="reporter",
        email="reporter@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add_all([reporter, owner])
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    db.add(video)
    db.commit()

    report = Report(
        reason="Test reason",
        reporter_id=reporter.id,
        video_id=video.id,
        created_at=date.today(),
        is_resolved=False,
    )
    db.add(report)
    db.commit()

    response = client.patch(f"/admin/report/{report.id}/resolve", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Report resolved successfully"
    assert data["report_id"] == report.id
    assert data["is_resolved"] is True

    response = client.patch(f"/admin/report/{report.id}/resolve", headers=admin_headers)
    assert response.status_code == 400
    assert "already resolved" in response.json()["detail"]

    response = client.patch("/admin/report/99999/resolve", headers=admin_headers)
    assert response.status_code == 404


def test_get_reports_with_details(client, db, admin_headers):
    reporter = User(
        username="reporter",
        email="reporter@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add_all([reporter, owner])
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    db.add(video)
    db.commit()

    report = Report(
        reason="Test reason",
        reporter_id=reporter.id,
        video_id=video.id,
        created_at=date.today(),
        is_resolved=False,
    )
    db.add(report)
    db.commit()

    response = client.get("/admin/reports/detailed", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert len(data["reports"]) == 1

    report_data = data["reports"][0]
    assert report_data["id"] == report.id
    assert report_data["reason"] == "Test reason"
    assert report_data["reporter"]["username"] == "reporter"
    assert report_data["video"]["title"] == "Test Video"


def test_get_problematic_users(client, db, admin_headers):
    problematic_user = User(
        username="problematic",
        email="problematic@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    normal_user = User(
        username="normal",
        email="normal@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add_all([problematic_user, normal_user, owner])
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    video = Video(
        title="Test Video",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    db.add(video)
    db.commit()

    for i in range(5):
        report = Report(
            reason=f"Spam {i}",
            reporter_id=problematic_user.id,
            video_id=video.id,
            created_at=date.today(),
            is_resolved=False,
        )
        db.add(report)

    for i in range(2):
        report = Report(
            reason=f"Valid concern {i}",
            reporter_id=normal_user.id,
            video_id=video.id,
            created_at=date.today(),
            is_resolved=False,
        )
        db.add(report)

    db.commit()

    response = client.get("/admin/users/problematic", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["min_reports_threshold"] == 3
    assert data["users"][0]["username"] == "problematic"
    assert data["users"][0]["reports_created"] == 5

    response = client.get(
        "/admin/users/problematic?min_reports=2", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["min_reports_threshold"] == 2


def test_get_channels_with_reports_analytics(client, db, admin_headers):
    owner = User(
        username="owner",
        email="owner@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    reporter = User(
        username="reporter",
        email="reporter@example.com",
        hashed_password="fake_hash",
        created_at=date.today(),
        is_moderator=False,
        is_deleted=False,
        is_banned=False,
    )
    db.add_all([owner, reporter])
    db.commit()

    channel = Channel(
        name="Test Channel",
        created_at=date.today(),
        owner_id=owner.id,
    )
    db.add(channel)
    db.commit()

    strike = ChannelStrike(
        channel_id=channel.id,
        duration=timedelta(days=7),
        video_id=None,
    )
    db.add(strike)
    db.commit()

    video1 = Video(
        title="Video 1",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    video2 = Video(
        title="Video 2",
        channel_id=channel.id,
        uploaded_at=date.today(),
    )
    db.add_all([video1, video2])
    db.commit()

    report1 = Report(
        reason="Issue 1",
        reporter_id=reporter.id,
        video_id=video1.id,
        created_at=date.today(),
        is_resolved=True,
    )
    report2 = Report(
        reason="Issue 2",
        reporter_id=reporter.id,
        video_id=video2.id,
        created_at=date.today(),
        is_resolved=False,
    )
    report3 = Report(
        reason="Issue 3",
        reporter_id=reporter.id,
        video_id=video1.id,
        created_at=date.today(),
        is_resolved=True,
    )
    db.add_all([report1, report2, report3])
    db.commit()

    response = client.get(
        "/admin/analytics/channels-reports-stats", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1

    analytics = data["analytics"][0]
    assert analytics["channel"]["name"] == "Test Channel"
    assert analytics["channel"]["strikes"] == 1
    assert analytics["channel"]["owner_username"] == "owner"
    assert analytics["report_stats"]["total_reports"] == 3
    assert analytics["report_stats"]["reported_videos_count"] == 2
    assert analytics["report_stats"]["unique_reporters"] == 1
    assert 66 <= analytics["report_stats"]["resolved_percentage"] <= 67
    assert analytics["risk_level"] in ["HIGH", "MEDIUM", "LOW"]

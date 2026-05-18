from __future__ import annotations

import pytest

from app.application.auth import AuthService
from app.application.dto.auth import LoginCommand
from app.application.user import UserService
from app.domain.errors import GoneError, NotFoundError, UnauthorizedError

class _FakeAuthRepo:
    @staticmethod
    def get_user_by_username(db, username: str):  # noqa: ANN001
        return None


def test_auth_login_raises_unauthorized_when_user_missing(monkeypatch):
    monkeypatch.setattr(
        "app.application.auth.AuthRepository",
        _FakeAuthRepo,
    )

    with pytest.raises(UnauthorizedError):
        AuthService.login_user(db=None, cmd=LoginCommand(username="x", password="y"))


def test_user_get_active_raises_not_found(monkeypatch):
    monkeypatch.setattr("app.application.user.UserRepository.get_by_id", lambda db, user_id: None)

    with pytest.raises(NotFoundError):
        UserService.get_active_user_or_404(db=None, user_id=123)


def test_user_get_active_raises_gone_when_deleted(monkeypatch):
    class _U:
        is_deleted = True

    monkeypatch.setattr("app.application.user.UserRepository.get_by_id", lambda db, user_id: _U())

    with pytest.raises(GoneError):
        UserService.get_active_user_or_404(db=None, user_id=123)

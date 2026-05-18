from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    username: str
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class LoginCommand:
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class UserView:
    id: int
    username: str
    email: str
    is_moderator: bool
    is_deleted: bool
    is_banned: bool
    created_at: str


@dataclass(frozen=True, slots=True)
class TokenView:
    access_token: str
    token_type: str = "bearer"

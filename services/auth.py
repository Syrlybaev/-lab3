"""Идентификация и аутентификация пользователей.

В объединённой версии проекта доступны два демо-варианта входа:
- по логину и постоянному паролю;
- по токену (как дополнительная демонстрация расширяемости).

Основной вариант для защиты лабораторной: постоянный пароль.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from data_sample import ROLE_LABELS, TOKENS, USERS


@dataclass(frozen=True)
class SessionUser:
    login: str
    full_name: str
    roles: tuple[str, ...]
    teacher_id: int | None
    departments: tuple[int, ...]
    group: str | None
    salary: int | None
    auth_method: str


class AuthService:
    def identify(self, login: str) -> bool:
        return login in USERS

    def authenticate_password(self, login: str, password: str) -> SessionUser | None:
        if not self.identify(login):
            return None
        user = USERS[login]
        if user["password"] != password:
            return None
        return self._build_session(login, user, "password")

    def authenticate_token(self, token: str) -> SessionUser | None:
        login = TOKENS.get(token)
        if login is None:
            return None
        return self._build_session(login, USERS[login], "token")

    def _build_session(self, login: str, user: dict, auth_method: str) -> SessionUser:
        return SessionUser(
            login=login,
            full_name=user["full_name"],
            roles=tuple(user["roles"]),
            teacher_id=user["teacher_id"],
            departments=tuple(user["departments"]),
            group=user.get("group"),
            salary=user.get("salary"),
            auth_method=auth_method,
        )

    @staticmethod
    def roles_as_text(roles: Iterable[str]) -> str:
        return ", ".join(ROLE_LABELS.get(role, role) for role in roles)

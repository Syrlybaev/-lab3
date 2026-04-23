from __future__ import annotations

from dataclasses import dataclass

from data_sample import ROLE_LABELS, USERS, hash_password


@dataclass(frozen=True)
class SessionUser:
    login: str
    full_name: str
    role: str
    student_id: int | None
    teacher_id: int | None
    auth_method: str


class AuthService:
    def identify(self, login: str) -> bool:
        return login in USERS

    def authenticate_password(self, login: str, password: str) -> SessionUser | None:
        if not self.identify(login):
            return None
        user = USERS[login]
        if not user["is_active"]:
            return None
        if user["password_hash"] != hash_password(password):
            return None
        return SessionUser(
            login=login,
            full_name=user["full_name"],
            role=user["role"],
            student_id=user["student_id"],
            teacher_id=user["teacher_id"],
            auth_method="password",
        )

    @staticmethod
    def role_as_text(role: str) -> str:
        return ROLE_LABELS.get(role, role)

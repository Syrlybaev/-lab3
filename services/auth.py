from __future__ import annotations

from dataclasses import dataclass

from services.database import DatabaseService
from services.utils import ROLE_LABELS, hash_password


@dataclass(frozen=True)
class SessionUser:
    login: str
    role: str
    full_name: str
    student_id: int | None
    teacher_id: int | None


class AuthService:
    def __init__(self) -> None:
        self.db = DatabaseService()

    def authenticate_password(self, login: str, password: str) -> SessionUser | None:
        user_data = self.db.get_user_by_login(login)
        if not user_data or not user_data['is_active']:
            return None
        
        if user_data['password_hash'] == hash_password(password):
            return SessionUser(
                login=user_data['login'],
                role=user_data['role'],
                full_name=user_data['full_name'],
                student_id=user_data['student_id'],
                teacher_id=user_data['teacher_id']
            )
        return None

    @staticmethod
    def role_as_text(role: str) -> str:
        return ROLE_LABELS.get(role, role)

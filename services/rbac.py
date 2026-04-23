from __future__ import annotations

from dataclasses import dataclass

from services.utils import ROLE_LABELS

ACL: dict[str, dict[str, set[str]]] = {
    "schedule": {
        "view":   {"student", "teacher", "administrator"},
        "edit":   {"administrator"},
    },
    "grades": {
        "view_own": {"student"},
        "view_all": {"teacher", "administrator", "accountant"},
        "edit":     {"teacher", "administrator"},
    },
    "students": {
        "view":   {"teacher", "administrator"},
        "manage": {"administrator"},
    },
    "teachers": {
        "view":   {"administrator"},
        "manage": {"administrator"},
    },
    "users": {
        "view":   {"administrator"},
        "manage": {"administrator"},
    },
    "finance": {
        "view_own": {"student"},
        "view_all": {"accountant", "administrator"},
        "manage":   {"accountant", "administrator"},
    },
}

MENU_SECTIONS: list[dict[str, str]] = [
    {"resource": "schedule", "title": "📅  Расписание"},
    {"resource": "grades",   "title": "📊  Оценки"},
    {"resource": "students", "title": "🎓  Студенты"},
    {"resource": "teachers", "title": "👨‍🏫  Преподаватели"},
    {"resource": "finance",  "title": "💰  Бухгалтерия"},
    {"resource": "users",    "title": "⚙️  Пользователи"},
]


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    matched_role: str | None


class RBACService:
    def check(self, role: str, resource: str, action: str) -> PermissionResult:
        allowed_roles = ACL.get(resource, {}).get(action, set())
        if role in allowed_roles:
            return PermissionResult(True, role)
        return PermissionResult(False, None)

    def can_open_section(self, role: str, resource: str) -> bool:
        actions = ACL.get(resource, {})
        return any(role in allowed_roles for allowed_roles in actions.values())

    def allowed_menu(self, role: str) -> list[dict[str, str]]:
        return [item for item in MENU_SECTIONS if self.can_open_section(role, item["resource"])]

    def role_title(self, role: str) -> str:
        return ROLE_LABELS.get(role, role)

    def explain_permissions(self, role: str) -> dict[str, list[str]]:
        permissions: dict[str, list[str]] = {}
        for resource, actions in ACL.items():
            allowed = [action for action, roles in actions.items() if role in roles]
            if allowed:
                permissions[resource] = allowed
        return permissions

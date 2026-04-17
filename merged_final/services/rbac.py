"""Ролевое управление доступом и ACL для объединённой версии приложения."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from data_sample import ROLE_LABELS

ROLE_HIERARCHY: dict[str, list[str]] = {
    "dean_admin": ["dispatcher", "head_of_department", "teacher", "student", "methodist", "accountant"],
    "head_of_department": ["teacher"],
    "methodist": ["dispatcher"],
    "dispatcher": [],
    "teacher": [],
    "student": [],
    "accountant": [],
}

ACL: dict[str, dict[str, set[str]]] = {
    "schedule": {
        "view": {"student", "teacher", "head_of_department", "dispatcher", "dean_admin", "methodist", "accountant"},
        "edit": {"dispatcher", "dean_admin", "methodist"},
        "publish": {"dispatcher", "dean_admin"},
        "reports": {"dispatcher", "head_of_department", "dean_admin"},
        "manage_replacements": {"dispatcher", "dean_admin"},
        "approve": {"head_of_department", "dean_admin"},
        "comment": {"head_of_department", "dean_admin"},
        "replacement_request": {"teacher", "dean_admin"},
    },
    "grades": {
        "view": {"student", "dean_admin", "teacher", "head_of_department", "methodist"},
        "edit": {"teacher", "methodist", "dean_admin"},
        "review": {"head_of_department", "dean_admin"},
    },
    "teachers": {
        "view_all": {"head_of_department", "dean_admin", "methodist"},
        "view_self": {"teacher", "dean_admin", "head_of_department"},
        "create_teacher": {"dean_admin"},
        "edit_teacher": {"dean_admin"},
        "assign_department": {"dean_admin", "head_of_department"},
        "assign_subject": {"dean_admin", "head_of_department"},
    },
    "users": {
        "view": {"dispatcher", "methodist", "dean_admin", "head_of_department"},
    },
    "finance": {
        "read_own_salary": {"teacher", "head_of_department", "dean_admin"},
        "read": {"accountant", "dean_admin"},
    },
}

MENU_ACTIONS: list[dict[str, str]] = [
    {"key": "schedule.view", "title": "Просмотр расписания"},
    {"key": "schedule.edit", "title": "Редактирование расписания"},
    {"key": "schedule.publish", "title": "Публикация расписания"},
    {"key": "schedule.reports", "title": "Просмотр отчётов"},
    {"key": "schedule.manage_replacements", "title": "Управление заменами"},
    {"key": "schedule.approve", "title": "Согласование расписания"},
    {"key": "schedule.comment", "title": "Отправка замечаний"},
    {"key": "schedule.replacement_request", "title": "Подача заявки на замену"},
    {"key": "grades.view", "title": "Просмотр успеваемости"},
    {"key": "grades.edit", "title": "Редактирование успеваемости"},
    {"key": "grades.review", "title": "Проверка успеваемости"},
    {"key": "teachers.open", "title": "Преподаватели"},
    {"key": "users.view", "title": "Пользователи"},
    {"key": "finance.read_own_salary", "title": "Моя зарплата"},
    {"key": "finance.read", "title": "Финансы"},
]


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    matched_role: str | None


class RBACService:
    def expand_roles(self, assigned_roles: Iterable[str]) -> set[str]:
        expanded: set[str] = set()
        stack = list(assigned_roles)
        while stack:
            role = stack.pop()
            if role in expanded:
                continue
            expanded.add(role)
            stack.extend(ROLE_HIERARCHY.get(role, []))
        return expanded

    def check(self, assigned_roles: Iterable[str], resource: str, action: str) -> PermissionResult:
        expanded = self.expand_roles(assigned_roles)
        allowed_roles = ACL.get(resource, {}).get(action, set())
        for role in expanded:
            if role in allowed_roles:
                return PermissionResult(True, role)
        return PermissionResult(False, None)

    def allowed_menu(self, assigned_roles: Iterable[str]) -> list[dict[str, str]]:
        visible: list[dict[str, str]] = []
        for item in MENU_ACTIONS:
            if item["key"] == "teachers.open":
                if self.check(assigned_roles, "teachers", "view_all").allowed or self.check(assigned_roles, "teachers", "view_self").allowed:
                    visible.append(item)
                continue
            resource, action = item["key"].split(".", 1)
            if self.check(assigned_roles, resource, action).allowed:
                visible.append(item)
        return visible

    def role_titles(self, roles: Iterable[str]) -> str:
        return ", ".join(ROLE_LABELS.get(role, role) for role in roles)

    def explain_permissions(self, roles: Iterable[str]) -> dict[str, list[str]]:
        expanded = self.expand_roles(roles)
        by_resource: dict[str, list[str]] = defaultdict(list)
        for resource, actions in ACL.items():
            for action, allowed_roles in actions.items():
                if expanded & allowed_roles:
                    by_resource[resource].append(action)
        return dict(by_resource)

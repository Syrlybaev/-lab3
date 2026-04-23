from __future__ import annotations
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def grade_label(m: int) -> str:
    """Оценка по одному модулю: 25-34 Удовл., 35-44 Хорошо, 45-54 Отлично."""
    if m <= 0:
        return "—"
    if m <= 34:
        return "Удовл."
    if m <= 44:
        return "Хорошо"
    return "Отлично"

def format_name_initials(full_name: str) -> str:
    if not full_name: return "—"
    parts = full_name.split()
    if len(parts) >= 3:
        return f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
    elif len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."
    return full_name

ROLE_LABELS: dict[str, str] = {
    "student":       "Студент",
    "teacher":       "Преподаватель",
    "administrator": "Администратор",
    "accountant":    "Бухгалтер",
}

DAY_ORDER: dict[str, int] = {
    "Понедельник": 1,
    "Вторник":     2,
    "Среда":       3,
    "Четверг":     4,
    "Пятница":     5,
    "Суббота":     6,
}

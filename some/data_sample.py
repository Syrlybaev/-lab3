"""data_sample.py — единая точка импорта данных.

Все данные хранятся в отдельных модулях внутри пакета data/.
Этот файл реэкспортирует всё, чтобы остальные модули могли
по-прежнему писать: from data_sample import STUDENTS, TEACHERS, ...
"""
from __future__ import annotations

from data.grades_data import GRADE_AUDIT, GRADE_RECORDS, grade_label
from data.finance_data import FINANCE_RECORDS, FINANCE_TYPES
from data.schedule_data import DAY_ORDER, PAIR_TIMES, SCHEDULE_DATA
from data.students_data import STUDENTS
from data.teachers_data import TEACHERS
from data.users_data import ROLE_LABELS, USERS, hash_password

__all__ = [
    "STUDENTS",
    "TEACHERS",
    "USERS",
    "ROLE_LABELS",
    "SCHEDULE_DATA",
    "DAY_ORDER",
    "PAIR_TIMES",
    "GRADE_RECORDS",
    "GRADE_AUDIT",
    "FINANCE_RECORDS",
    "FINANCE_TYPES",
    "grade_label",
    "hash_password",
]

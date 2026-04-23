from __future__ import annotations

# Система оценивания: M1 и M2 по 25–54 баллов
# Итоговый: M1+M2 (50–108 условно, но здесь хранятся отдельно)
# Оценка по баллу: 25–34 → Удовл., 35–44 → Хорошо, 45–54 → Отлично

GRADE_RECORDS: list[dict] = [
    # ── 2026 весна ── ИДБ-23-13 ──
    {"id":  1, "student_id":  1, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 48, "m2": 47, "coefficient": 2.8, "date": "2026-04-16", "status": "Подтверждена"},
    {"id":  2, "student_id":  1, "teacher_id": 1, "subject": "Базы данных",               "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Лабораторная работа","attempt": 1, "m1": 45, "m2": 46, "coefficient": 2.1, "date": "2026-04-12", "status": "Подтверждена"},
    {"id":  3, "student_id":  1, "teacher_id": 2, "subject": "Web-технологии",            "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 43, "m2": 44, "coefficient": 2.4, "date": "2026-04-17", "status": "Подтверждена"},
    {"id":  4, "student_id":  1, "teacher_id": 3, "subject": "Дискретная математика",     "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 36, "m2": 38, "coefficient": 2.5, "date": "2026-04-20", "status": "Подтверждена"},
    {"id":  5, "student_id":  1, "teacher_id": 7, "subject": "Теория вероятностей",       "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 40, "m2": 41, "coefficient": 2.3, "date": "2026-04-22", "status": "Подтверждена"},

    {"id":  6, "student_id":  2, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 36, "m2": 37, "coefficient": 2.8, "date": "2026-04-16", "status": "Подтверждена"},
    {"id":  7, "student_id":  2, "teacher_id": 2, "subject": "Программирование",          "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 2, "m1": 28, "m2": 30, "coefficient": 1.6, "date": "2026-04-18", "status": "Пересдача"},
    {"id":  8, "student_id":  2, "teacher_id": 3, "subject": "Дискретная математика",     "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 32, "m2": 31, "coefficient": 2.5, "date": "2026-04-20", "status": "Подтверждена"},
    {"id":  9, "student_id":  2, "teacher_id": 7, "subject": "Теория вероятностей",       "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 38, "m2": 37, "coefficient": 2.3, "date": "2026-04-22", "status": "Подтверждена"},

    {"id": 10, "student_id":  3, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 50, "m2": 52, "coefficient": 2.8, "date": "2026-04-16", "status": "Подтверждена"},
    {"id": 11, "student_id":  3, "teacher_id": 2, "subject": "Web-технологии",            "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 47, "m2": 49, "coefficient": 2.4, "date": "2026-04-17", "status": "Подтверждена"},
    {"id": 12, "student_id":  3, "teacher_id": 6, "subject": "Операционные системы",      "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Лабораторная работа","attempt": 1, "m1": 44, "m2": 45, "coefficient": 2.2, "date": "2026-04-19", "status": "Подтверждена"},

    {"id": 13, "student_id":  4, "teacher_id": 1, "subject": "Базы данных",               "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Лабораторная работа","attempt": 1, "m1": 39, "m2": 40, "coefficient": 2.1, "date": "2026-04-12", "status": "Подтверждена"},
    {"id": 14, "student_id":  4, "teacher_id": 3, "subject": "Дискретная математика",     "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 27, "m2": 26, "coefficient": 2.5, "date": "2026-04-20", "status": "Подтверждена"},

    {"id": 15, "student_id":  5, "teacher_id": 2, "subject": "Программирование",          "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 46, "m2": 48, "coefficient": 1.6, "date": "2026-04-18", "status": "Подтверждена"},
    {"id": 16, "student_id":  5, "teacher_id": 7, "subject": "Теория вероятностей",       "group": "ИДБ-23-13", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 35, "m2": 36, "coefficient": 2.3, "date": "2026-04-22", "status": "Подтверждена"},

    # ── 2026 весна ── ИДБ-23-14 ──
    {"id": 17, "student_id":  7, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 51, "m2": 53, "coefficient": 2.8, "date": "2026-04-14", "status": "Подтверждена"},
    {"id": 18, "student_id":  7, "teacher_id": 2, "subject": "Web-технологии",            "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 45, "m2": 47, "coefficient": 2.4, "date": "2026-04-15", "status": "Подтверждена"},
    {"id": 19, "student_id":  7, "teacher_id": 3, "subject": "Дискретная математика",     "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 42, "m2": 43, "coefficient": 2.5, "date": "2026-04-21", "status": "Подтверждена"},

    {"id": 20, "student_id":  8, "teacher_id": 3, "subject": "Дискретная математика",     "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 25, "m2": 25, "coefficient": 2.5, "date": "2026-04-10", "status": "Неявка"},
    {"id": 21, "student_id":  8, "teacher_id": 1, "subject": "Базы данных",               "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Лабораторная работа","attempt": 2, "m1": 30, "m2": 29, "coefficient": 2.1, "date": "2026-04-18", "status": "Пересдача"},

    {"id": 22, "student_id":  9, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 44, "m2": 43, "coefficient": 2.8, "date": "2026-04-14", "status": "Подтверждена"},
    {"id": 23, "student_id":  9, "teacher_id": 7, "subject": "Теория вероятностей",       "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 38, "m2": 39, "coefficient": 2.3, "date": "2026-04-22", "status": "Подтверждена"},

    {"id": 24, "student_id": 10, "teacher_id": 2, "subject": "Web-технологии",            "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 40, "m2": 42, "coefficient": 2.4, "date": "2026-04-15", "status": "Подтверждена"},
    {"id": 25, "student_id": 10, "teacher_id": 6, "subject": "Операционные системы",      "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 36, "m2": 37, "coefficient": 2.2, "date": "2026-04-19", "status": "Подтверждена"},

    {"id": 26, "student_id": 11, "teacher_id": 5, "subject": "Экономика предприятия",     "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 48, "m2": 50, "coefficient": 1.8, "date": "2026-04-23", "status": "Подтверждена"},
    {"id": 27, "student_id": 11, "teacher_id": 3, "subject": "Дискретная математика",     "group": "ИДБ-23-14", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 43, "m2": 44, "coefficient": 2.5, "date": "2026-04-21", "status": "Подтверждена"},

    # ── 2025 осень ── ИДБ-23-13 ──
    {"id": 28, "student_id":  1, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-13", "semester": "2025 осень", "control_type": "Экзамен",          "attempt": 1, "m1": 44, "m2": 43, "coefficient": 2.8, "date": "2026-01-15", "status": "Подтверждена"},
    {"id": 29, "student_id":  1, "teacher_id": 3, "subject": "Математический анализ",    "group": "ИДБ-23-13", "semester": "2025 осень", "control_type": "Экзамен",          "attempt": 1, "m1": 38, "m2": 37, "coefficient": 2.6, "date": "2026-01-18", "status": "Подтверждена"},
    {"id": 30, "student_id":  2, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-13", "semester": "2025 осень", "control_type": "Экзамен",          "attempt": 1, "m1": 33, "m2": 32, "coefficient": 2.8, "date": "2026-01-15", "status": "Подтверждена"},
    {"id": 31, "student_id":  3, "teacher_id": 1, "subject": "Базы данных",               "group": "ИДБ-23-13", "semester": "2025 осень", "control_type": "Лабораторная работа","attempt": 1, "m1": 49, "m2": 51, "coefficient": 2.1, "date": "2026-01-20", "status": "Подтверждена"},

    # ── 2025 весна ── ИДБ-23-13 ──
    {"id": 32, "student_id":  1, "teacher_id": 3, "subject": "Дискретная математика",     "group": "ИДБ-23-13", "semester": "2025 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 35, "m2": 34, "coefficient": 2.5, "date": "2025-06-10", "status": "Подтверждена"},
    {"id": 33, "student_id":  2, "teacher_id": 2, "subject": "Web-технологии",            "group": "ИДБ-23-13", "semester": "2025 весна", "control_type": "Зачет",            "attempt": 1, "m1": 37, "m2": 38, "coefficient": 2.4, "date": "2025-06-12", "status": "Подтверждена"},

    # ── 2026 весна ── ИДБ-23-15 ──
    {"id": 34, "student_id": 12, "teacher_id": 6, "subject": "Компьютерные сети",         "group": "ИДБ-23-15", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 46, "m2": 47, "coefficient": 2.2, "date": "2026-04-18", "status": "Подтверждена"},
    {"id": 35, "student_id": 12, "teacher_id": 7, "subject": "Математическая статистика", "group": "ИДБ-23-15", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 42, "m2": 43, "coefficient": 2.3, "date": "2026-04-20", "status": "Подтверждена"},
    {"id": 36, "student_id": 13, "teacher_id": 1, "subject": "Информационные системы",   "group": "ИДБ-23-15", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 50, "m2": 51, "coefficient": 2.8, "date": "2026-04-16", "status": "Подтверждена"},
    {"id": 37, "student_id": 14, "teacher_id": 5, "subject": "Менеджмент",                "group": "ИДБ-23-15", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 38, "m2": 37, "coefficient": 1.8, "date": "2026-04-23", "status": "Подтверждена"},
    {"id": 38, "student_id": 15, "teacher_id": 2, "subject": "Web-технологии",            "group": "ИДБ-23-15", "semester": "2026 весна", "control_type": "Лабораторная работа","attempt": 1, "m1": 44, "m2": 45, "coefficient": 2.4, "date": "2026-04-17", "status": "Подтверждена"},
    {"id": 39, "student_id": 16, "teacher_id": 6, "subject": "Компьютерные сети",         "group": "ИДБ-23-15", "semester": "2026 весна", "control_type": "Зачет",            "attempt": 1, "m1": 29, "m2": 28, "coefficient": 2.2, "date": "2026-04-18", "status": "Пересдача"},
    {"id": 40, "student_id": 16, "teacher_id": 7, "subject": "Математическая статистика", "group": "ИДБ-23-15", "semester": "2026 весна", "control_type": "Экзамен",          "attempt": 1, "m1": 25, "m2": 25, "coefficient": 2.3, "date": "2026-04-20", "status": "Неявка"},
]

GRADE_AUDIT: list[dict] = [
    {"grade_id":  7, "changed_by": "teacher_kozlova", "old_m1": 25, "old_m2": 25, "new_m1": 28, "new_m2": 30, "changed_at": "2026-04-18 14:20", "comment": "Пересдача после доработки"},
    {"grade_id": 20, "changed_by": "admin_demo",       "old_m1": 30, "old_m2": 30, "new_m1": 25, "new_m2": 25, "changed_at": "2026-04-10 18:00", "comment": "Статус изменён на неявку по заявлению деканата"},
]


def grade_label(m: int) -> str:
    """Оценка по одному модулю: 25-34 Удовл., 35-44 Хорошо, 45-54 Отлично."""
    if m <= 0:
        return "—"
    if m <= 34:
        return "Удовл."
    if m <= 44:
        return "Хорошо"
    return "Отлично"

from __future__ import annotations

DAY_ORDER: dict[str, int] = {
    "Понедельник": 1,
    "Вторник": 2,
    "Среда": 3,
    "Четверг": 4,
    "Пятница": 5,
    "Суббота": 6,
}

PAIR_TIMES: dict[int, str] = {
    1: "08:30–10:10",
    2: "10:20–12:00",
    3: "12:20–14:00",
    4: "14:10–15:50",
    5: "16:00–17:40",
}

# lesson_type: Лекция | Семинар | Лабораторная | Дистант
# format: Очная | Дистанционная
# room: пустая строка → нет аудитории (дистант или спортзал прописан явно)
# date_start / date_end — период проведения занятий

SCHEDULE_DATA: list[dict] = [

    # ══════════════════════════════════════════
    # ИДБ-23-13  ПОНЕДЕЛЬНИК
    # ══════════════════════════════════════════
    {"day": "Понедельник", "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-13", "subject": "Информационные системы",  "teacher_id": 1, "room": "201",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Понедельник", "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-13", "subject": "Базы данных",             "teacher_id": 1, "room": "104",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "19.02.2026", "date_end": "15.04.2026"},
    {"day": "Понедельник", "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-13", "subject": "Web-технологии",          "teacher_id": 2, "room": "307",      "lesson_type": "Лабораторная","format": "Очная",         "date_start": "12.02.2026", "date_end": "25.04.2026"},
    {"day": "Понедельник", "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-13", "subject": "Физическая культура",     "teacher_id": 4, "room": "Спортзал","lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},

    # ══════════════════════════════════════════
    # ИДБ-23-13  ВТОРНИК
    # ══════════════════════════════════════════
    {"day": "Вторник",    "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-13", "subject": "Дискретная математика",   "teacher_id": 3, "room": "115",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Вторник",    "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-13", "subject": "Базы данных",             "teacher_id": 1, "room": "307",      "lesson_type": "Лабораторная","format": "Очная",         "date_start": "12.02.2026", "date_end": "15.04.2026"},
    {"day": "Вторник",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-13", "subject": "Операционные системы",   "teacher_id": 6, "room": "210",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "19.02.2026", "date_end": "02.05.2026"},
    {"day": "Вторник",    "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-13", "subject": "Программирование",        "teacher_id": 2, "room": "",         "lesson_type": "Дистант",     "format": "Дистанционная", "date_start": "26.02.2026", "date_end": "18.04.2026"},

    # ══════════════════════════════════════════
    # ИДБ-23-13  СРЕДА
    # ══════════════════════════════════════════
    {"day": "Среда",      "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-13", "subject": "Информационные системы",  "teacher_id": 1, "room": "115",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "25.04.2026"},
    {"day": "Среда",      "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-13", "subject": "Математический анализ",   "teacher_id": 3, "room": "201",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Среда",      "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-13", "subject": "Web-технологии",          "teacher_id": 2, "room": "307",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "18.04.2026"},
    {"day": "Среда",      "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-13", "subject": "Теория вероятностей",     "teacher_id": 7, "room": "",         "lesson_type": "Дистант",     "format": "Дистанционная", "date_start": "19.02.2026", "date_end": "02.05.2026"},

    # ══════════════════════════════════════════
    # ИДБ-23-13  ЧЕТВЕРГ
    # ══════════════════════════════════════════
    {"day": "Четверг",    "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-13", "subject": "Операционные системы",   "teacher_id": 6, "room": "104",      "lesson_type": "Лабораторная","format": "Очная",         "date_start": "19.02.2026", "date_end": "25.04.2026"},
    {"day": "Четверг",    "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-13", "subject": "Дискретная математика",   "teacher_id": 3, "room": "201",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Четверг",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-13", "subject": "Экономика предприятия",   "teacher_id": 5, "room": "118",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "26.02.2026", "date_end": "02.05.2026"},
    {"day": "Четверг",    "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-13", "subject": "Физическая культура",     "teacher_id": 4, "room": "Спортзал","lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},

    # ══════════════════════════════════════════
    # ИДБ-23-13  ПЯТНИЦА
    # ══════════════════════════════════════════
    {"day": "Пятница",    "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-13", "subject": "Программирование",        "teacher_id": 2, "room": "307",      "lesson_type": "Лабораторная","format": "Очная",         "date_start": "12.02.2026", "date_end": "18.04.2026"},
    {"day": "Пятница",    "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-13", "subject": "Теория вероятностей",     "teacher_id": 7, "room": "201",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Пятница",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-13", "subject": "Компьютерные сети",       "teacher_id": 6, "room": "210",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "19.02.2026", "date_end": "25.04.2026"},
    {"day": "Пятница",    "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-13", "subject": "Экономика предприятия",   "teacher_id": 5, "room": "",         "lesson_type": "Дистант",     "format": "Дистанционная", "date_start": "26.02.2026", "date_end": "02.05.2026"},

    # ══════════════════════════════════════════
    # ИДБ-23-14
    # ══════════════════════════════════════════
    {"day": "Понедельник","pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-14", "subject": "Информационные системы",  "teacher_id": 1, "room": "201",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Понедельник","pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-14", "subject": "Web-технологии",          "teacher_id": 2, "room": "307",      "lesson_type": "Лабораторная","format": "Очная",         "date_start": "12.02.2026", "date_end": "25.04.2026"},
    {"day": "Понедельник","pair": 5, "time": PAIR_TIMES[5], "group": "ИДБ-23-14", "subject": "Физическая культура",     "teacher_id": 4, "room": "Спортзал","lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Вторник",    "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-14", "subject": "Дискретная математика",   "teacher_id": 3, "room": "115",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Вторник",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-14", "subject": "Теория вероятностей",     "teacher_id": 7, "room": "201",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "19.02.2026", "date_end": "02.05.2026"},
    {"day": "Среда",      "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-14", "subject": "Операционные системы",   "teacher_id": 6, "room": "210",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "19.02.2026", "date_end": "02.05.2026"},
    {"day": "Среда",      "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-14", "subject": "Web-технологии",          "teacher_id": 2, "room": "307",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "18.04.2026"},
    {"day": "Четверг",    "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-14", "subject": "Базы данных",             "teacher_id": 1, "room": "104",      "lesson_type": "Лабораторная","format": "Очная",         "date_start": "12.02.2026", "date_end": "15.04.2026"},
    {"day": "Четверг",    "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-14", "subject": "Экономика предприятия",   "teacher_id": 5, "room": "118",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "26.02.2026", "date_end": "02.05.2026"},
    {"day": "Пятница",    "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-14", "subject": "Дискретная математика",   "teacher_id": 3, "room": "115",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "25.04.2026"},
    {"day": "Пятница",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-14", "subject": "Программирование",        "teacher_id": 2, "room": "",         "lesson_type": "Дистант",     "format": "Дистанционная", "date_start": "12.02.2026", "date_end": "18.04.2026"},

    # ══════════════════════════════════════════
    # ИДБ-23-15
    # ══════════════════════════════════════════
    {"day": "Понедельник","pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-15", "subject": "Компьютерные сети",       "teacher_id": 6, "room": "210",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Понедельник","pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-15", "subject": "Математическая статистика","teacher_id": 7,"room": "201",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Понедельник","pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-15", "subject": "Физическая культура",     "teacher_id": 4, "room": "Спортзал","lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Вторник",    "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-15", "subject": "Web-технологии",          "teacher_id": 2, "room": "307",      "lesson_type": "Лабораторная","format": "Очная",         "date_start": "12.02.2026", "date_end": "25.04.2026"},
    {"day": "Вторник",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-15", "subject": "Менеджмент",              "teacher_id": 5, "room": "118",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "26.02.2026", "date_end": "02.05.2026"},
    {"day": "Среда",      "pair": 2, "time": PAIR_TIMES[2], "group": "ИДБ-23-15", "subject": "Компьютерные сети",       "teacher_id": 6, "room": "210",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "19.02.2026", "date_end": "25.04.2026"},
    {"day": "Среда",      "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-15", "subject": "Математическая статистика","teacher_id": 7,"room": "",         "lesson_type": "Дистант",     "format": "Дистанционная", "date_start": "19.02.2026", "date_end": "02.05.2026"},
    {"day": "Четверг",    "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-15", "subject": "Информационные системы",  "teacher_id": 1, "room": "201",      "lesson_type": "Лекция",      "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
    {"day": "Четверг",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-15", "subject": "Web-технологии",          "teacher_id": 2, "room": "307",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "18.04.2026"},
    {"day": "Пятница",    "pair": 1, "time": PAIR_TIMES[1], "group": "ИДБ-23-15", "subject": "Информационные системы",  "teacher_id": 1, "room": "115",      "lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "25.04.2026"},
    {"day": "Пятница",    "pair": 3, "time": PAIR_TIMES[3], "group": "ИДБ-23-15", "subject": "Менеджмент",              "teacher_id": 5, "room": "",         "lesson_type": "Дистант",     "format": "Дистанционная", "date_start": "26.02.2026", "date_end": "02.05.2026"},
    {"day": "Пятница",    "pair": 4, "time": PAIR_TIMES[4], "group": "ИДБ-23-15", "subject": "Физическая культура",     "teacher_id": 4, "room": "Спортзал","lesson_type": "Семинар",     "format": "Очная",         "date_start": "12.02.2026", "date_end": "02.05.2026"},
]

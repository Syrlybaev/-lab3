"""Общие демо-данные приложения "Виртуальный деканат".

Файл объединяет:
- функционал расписания и успеваемости из версии одногруппницы;
- модуль "Преподаватели" для локального представления 4;
- дополнительные роли и данные для общего командного приложения.
"""

PAIR_TIMES = {
    1: "8:30-10:10",
    2: "10:20-12:00",
    3: "12:20-14:00",
    4: "14:10-15:50",
    5: "16:00-17:40",
    6: "18:00-19:30",
    7: "19:40-21:00",
    8: "21:20-22:50",
}

ROLE_LABELS = {
    "dispatcher": "Диспетчерская служба",
    "head_of_department": "Заведующий кафедрой",
    "teacher": "Преподаватель",
    "student": "Студент",
    "methodist": "Методист",
    "accountant": "Бухгалтерия",
    "dean_admin": "Администратор",
}

USERS = {
    # Сохранены исходные логины и пароли одногруппницы
    "dispetcher": {
        "password": "123",
        "roles": ["dispatcher"],
        "full_name": "Петрова А.С.",
        "teacher_id": None,
        "departments": [],
        "group": None,
        "salary": None,
    },
    "zav_kaf": {
        "password": "456",
        "roles": ["head_of_department"],
        "full_name": "Сидоров И.И.",
        "teacher_id": 2,
        "departments": [1],
        "group": None,
        "salary": 90000,
    },
    "teacher": {
        "password": "789",
        "roles": ["teacher"],
        "full_name": "Иванов В.В.",
        "teacher_id": 1,
        "departments": [1, 2],
        "group": None,
        "salary": 85000,
    },
    "student": {
        "password": "000",
        "roles": ["student"],
        "full_name": "Смирнова Е.А.",
        "teacher_id": None,
        "departments": [],
        "group": "ИВТ-41",
        "salary": None,
    },
    # Дополнительные роли из новой версии main.py
    "methodist": {
        "password": "111",
        "roles": ["methodist"],
        "full_name": "Козлова М.И.",
        "teacher_id": None,
        "departments": [],
        "group": None,
        "salary": None,
    },
    "accountant": {
        "password": "222",
        "roles": ["accountant"],
        "full_name": "Соколова Т.П.",
        "teacher_id": None,
        "departments": [],
        "group": None,
        "salary": None,
    },
    # Общий администратор для командного приложения
    "dean_admin": {
        "password": "999",
        "roles": ["dean_admin"],
        "full_name": "Кузнецова Н.М.",
        "teacher_id": None,
        "departments": [1, 2, 3],
        "group": None,
        "salary": None,
    },
}

TOKENS = {
    "TOKEN_123": "dispetcher",
    "TOKEN_456": "teacher",
    "TOKEN_789": "student",
}

SCHEDULE_DATA = [
    {"day": "Понедельник", "date": "07.04", "pair": 1, "time": PAIR_TIMES[1],
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Математика", "room": "0211", "teacher": "Проф. Иванов", "type": "Лекция", "format": "Очно"},
    {"day": "Понедельник", "date": "07.04", "pair": 2, "time": PAIR_TIMES[2],
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Физика", "room": "0304", "teacher": "Доц. Петров", "type": "Лабораторная", "format": "Очно"},
    {"day": "Понедельник", "date": "07.04", "pair": 3, "time": PAIR_TIMES[3],
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Английский язык", "room": "401", "teacher": "Ст. Денисова", "type": "Семинар", "format": "Очно"},
    {"day": "Вторник", "date": "08.04", "pair": 1, "time": PAIR_TIMES[1],
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Программирование", "room": "0211", "teacher": "Проф. Сидоров", "type": "Лекция", "format": "Дистант"},
    {"day": "Вторник", "date": "08.04", "pair": 3, "time": PAIR_TIMES[3],
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Базы данных", "room": "401", "teacher": "Доц. Смирнова", "type": "Лабораторная", "format": "Очно"},
    {"day": "Вторник", "date": "08.04", "pair": 4, "time": PAIR_TIMES[4],
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Web-технологии", "room": "0304", "teacher": "Проф. Козлов", "type": "Семинар", "format": "Очно"},
    {"day": "Среда", "date": "09.04", "pair": 1, "time": PAIR_TIMES[1],
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Компьютерные сети", "room": "0211", "teacher": "Доц. Воробьёва", "type": "Лекция", "format": "Очно"},
    {"day": "Среда", "date": "09.04", "pair": 3, "time": PAIR_TIMES[3],
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Информационная безопасность", "room": "401", "teacher": "Проф. Соколов", "type": "Лабораторная", "format": "Очно"},
    {"day": "Среда", "date": "09.04", "pair": 5, "time": PAIR_TIMES[5],
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Операционные системы", "room": "0304", "teacher": "Проф. Новиков", "type": "Семинар", "format": "Дистант"},
    {"day": "Четверг", "date": "10.04", "pair": 2, "time": PAIR_TIMES[2],
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Дискретная математика", "room": "0211", "teacher": "Доц. Морозова", "type": "Лекция", "format": "Очно"},
    {"day": "Четверг", "date": "10.04", "pair": 4, "time": PAIR_TIMES[4],
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Экономика", "room": "401", "teacher": "Доц. Лебедева", "type": "Семинар", "format": "Очно"},
    {"day": "Четверг", "date": "10.04", "pair": 5, "time": PAIR_TIMES[5],
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Методология науки", "room": "0211", "teacher": "Проф. Андреев", "type": "Лекция", "format": "Очно"},
    {"day": "Пятница", "date": "11.04", "pair": 1, "time": PAIR_TIMES[1],
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Машинное обучение", "room": "0211", "teacher": "Проф. Орлов", "type": "Лекция", "format": "Дистант"},
    {"day": "Пятница", "date": "11.04", "pair": 4, "time": PAIR_TIMES[4],
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Анализ данных", "room": "0304", "teacher": "Доц. Крылова", "type": "Лабораторная", "format": "Очно"},
    {"day": "Суббота", "date": "12.04", "pair": 1, "time": PAIR_TIMES[1],
     "period_start": "10.02", "period_end": "31.05",
     "subject": "Физическая культура", "room": "Спортзал", "teacher": "Ст. Орлов", "type": "Семинар", "format": "Очно"},
    {"day": "Суббота", "date": "12.04", "pair": 2, "time": PAIR_TIMES[2],
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Управление проектами", "room": "401", "teacher": "Доц. Белова", "type": "Семинар", "format": "Очно"},
    {"day": "Суббота", "date": "12.04", "pair": 3, "time": PAIR_TIMES[3],
     "period_start": "10.02", "period_end": "31.05",
     "subject": "Психология", "room": "0211", "teacher": "Доц. Михайлова", "type": "Лекция", "format": "Очно"},
    {"day": "Суббота", "date": "12.04", "pair": 4, "time": PAIR_TIMES[4],
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Риторика", "room": "401", "teacher": "Ст. Павлова", "type": "Семинар", "format": "Очно"},
    {"day": "Суббота", "date": "12.04", "pair": 5, "time": PAIR_TIMES[5],
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Правоведение", "room": "0304", "teacher": "Проф. Степанов", "type": "Лекция", "format": "Дистант"},
]

GRADES_DATA = {
    "2025 - осень": [
        {"subject": "Математика", "m1": 38, "m2": 42, "exam": 40, "credit": None, "coefficient": 2.5},
        {"subject": "Физика", "m1": 35, "m2": 36, "exam": None, "credit": 48, "coefficient": 2.0},
        {"subject": "Программирование", "m1": 45, "m2": 48, "exam": 50, "credit": None, "coefficient": 3.0},
    ],
    "2026 - весна": [
        {"subject": "Информационные системы", "m1": 42, "m2": 48, "exam": 50, "credit": None, "coefficient": 2.8},
        {"subject": "Базы данных", "m1": 38, "m2": 40, "exam": 45, "credit": None, "coefficient": 2.5},
        {"subject": "Web-технологии", "m1": 35, "m2": 38, "exam": None, "credit": 42, "coefficient": 2.2},
        {"subject": "Машинное обучение", "m1": 40, "m2": 42, "exam": 48, "credit": None, "coefficient": 3.0},
        {"subject": "Анализ данных", "m1": 36, "m2": 39, "exam": None, "credit": 44, "coefficient": 2.6},
        {"subject": "Управление проектами", "m1": 32, "m2": 35, "exam": None, "credit": 38, "coefficient": 1.5},
        {"subject": "Физическая культура", "m1": 40, "m2": 42, "exam": None, "credit": 45, "coefficient": 1.0},
        {"subject": "Компьютерные сети", "m1": 41, "m2": 43, "exam": 46, "credit": None, "coefficient": 2.7},
        {"subject": "Операционные системы", "m1": 33, "m2": 36, "exam": None, "credit": 40, "coefficient": 2.4},
        {"subject": "Психология", "m1": 40, "m2": 42, "exam": None, "credit": 48, "coefficient": 1.8},
        {"subject": "Методология науки", "m1": 44, "m2": 45, "exam": 49, "credit": None, "coefficient": 2.9},
    ],
    "2026 - осень": [
        {"subject": "Риторика", "m1": 38, "m2": 40, "exam": None, "credit": 42, "coefficient": 1.2},
        {"subject": "Правоведение", "m1": 35, "m2": 37, "exam": 41, "credit": None, "coefficient": 2.1},
        {"subject": "Дипломное проектирование", "m1": None, "m2": None, "exam": None, "credit": 50, "coefficient": 0.8},
    ],
}

INSTITUTES = [
    {"id": 1, "name": "Институт информационных технологий", "description": "ИТ-направления подготовки"},
    {"id": 2, "name": "Институт цифрового производства", "description": "Технологические и инженерные направления"},
]

DEPARTMENTS = [
    {"id": 1, "name": "Кафедра информационных систем", "institute_id": 1},
    {"id": 2, "name": "Кафедра прикладной математики", "institute_id": 1},
    {"id": 3, "name": "Кафедра управления проектами", "institute_id": 2},
]

POSITIONS = [
    {"id": 1, "name": "Профессор", "description": "Научно-педагогический работник высшей квалификации"},
    {"id": 2, "name": "Доцент", "description": "Преподаватель, ведущий лекции и практики"},
    {"id": 3, "name": "Старший преподаватель", "description": "Ведет практические и лабораторные занятия"},
]

DEGREES = [
    {"id": 1, "name": "д.т.н.", "description": "Доктор технических наук"},
    {"id": 2, "name": "к.т.н.", "description": "Кандидат технических наук"},
    {"id": 3, "name": "без степени", "description": "Учёная степень отсутствует"},
]

TEACHERS = [
    {"id": 1, "last_name": "Иванов", "first_name": "Виктор", "patronymic": "Викторович", "email": "ivanov@vdekanat.local", "phone": "79000000001", "degree_id": 1},
    {"id": 2, "last_name": "Сидоров", "first_name": "Илья", "patronymic": "Игоревич", "email": "sidorov@vdekanat.local", "phone": "79000000002", "degree_id": 2},
    {"id": 3, "last_name": "Петров", "first_name": "Андрей", "patronymic": "Сергеевич", "email": "petrov@vdekanat.local", "phone": "79000000003", "degree_id": 2},
    {"id": 4, "last_name": "Морозова", "first_name": "Елена", "patronymic": "Павловна", "email": "morozova@vdekanat.local", "phone": "79000000004", "degree_id": 3},
]

# Исправление по замечанию пользователя: преподаватель может работать на нескольких кафедрах.
TEACHER_DEPARTMENTS = [
    {"teacher_id": 1, "department_id": 1},
    {"teacher_id": 1, "department_id": 2},
    {"teacher_id": 2, "department_id": 1},
    {"teacher_id": 3, "department_id": 3},
    {"teacher_id": 4, "department_id": 2},
]

TEACHER_POSITIONS = [
    {"teacher_id": 1, "position_id": 1},
    {"teacher_id": 2, "position_id": 2},
    {"teacher_id": 3, "position_id": 2},
    {"teacher_id": 4, "position_id": 3},
]

SUBJECTS = [
    {"id": 1, "code": "IS-301", "name": "Информационные системы", "department_id": 1, "hours_per_semester": 72},
    {"id": 2, "code": "DB-202", "name": "Базы данных", "department_id": 1, "hours_per_semester": 68},
    {"id": 3, "code": "PM-110", "name": "Прикладная математика", "department_id": 2, "hours_per_semester": 64},
    {"id": 4, "code": "PMGT-410", "name": "Управление проектами", "department_id": 3, "hours_per_semester": 54},
]

TEACHER_SUBJECTS = [
    {"id": 1, "teacher_id": 1, "subject_id": 1, "semester": "2026-1", "description": "Лекции"},
    {"id": 2, "teacher_id": 1, "subject_id": 3, "semester": "2026-1", "description": "Практика"},
    {"id": 3, "teacher_id": 2, "subject_id": 2, "semester": "2026-1", "description": "Лекции и лабораторные"},
    {"id": 4, "teacher_id": 3, "subject_id": 4, "semester": "2026-1", "description": "Лекции"},
    {"id": 5, "teacher_id": 4, "subject_id": 3, "semester": "2026-1", "description": "Практика"},
]

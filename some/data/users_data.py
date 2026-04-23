from __future__ import annotations

import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


ROLE_LABELS: dict[str, str] = {
    "student":       "Студент",
    "teacher":       "Преподаватель",
    "administrator": "Администратор",
    "accountant":    "Бухгалтер",
}

USERS: dict[str, dict] = {
    # ── Студенты ──
    "student_demo": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Смирнова Елена Андреевна",
        "student_id": 1,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_kuznetsov": {
        "password_hash": hash_password("kuz2026"),
        "role": "student", "full_name": "Кузнецов Артём Сергеевич",
        "student_id": 2,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-05",
    },
    "student_petrov": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Петров Дмитрий Игоревич",
        "student_id": 3,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_zaharova": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Захарова Ксения Павловна",
        "student_id": 4,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_volkov": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Волков Никита Романович",
        "student_id": 5,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_novikova": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Новикова Анастасия Юрьевна",
        "student_id": 6,  "teacher_id": None, "is_active": False, "last_password_change": "2026-02-15",
    },
    "student_orlova": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Орлова Мария Дмитриевна",
        "student_id": 7,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_fedorov": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Фёдоров Илья Павлович",
        "student_id": 8,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_sokolova": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Соколова Виктория Алексеевна",
        "student_id": 9,  "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_morozov": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Морозов Евгений Олегович",
        "student_id": 10, "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    "student_popov": {
        "password_hash": hash_password("stud2026"),
        "role": "student", "full_name": "Попов Александр Николаевич",
        "student_id": 12, "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
    # ── Преподаватели ──
    "teacher_demo": {
        "password_hash": hash_password("teach2026"),
        "role": "teacher", "full_name": "Иванов Виктор Викторович",
        "student_id": None, "teacher_id": 1, "is_active": True, "last_password_change": "2026-03-29",
    },
    "teacher_kozlova": {
        "password_hash": hash_password("koz2026"),
        "role": "teacher", "full_name": "Козлова Марина Игоревна",
        "student_id": None, "teacher_id": 2, "is_active": True, "last_password_change": "2026-04-10",
    },
    "teacher_sidorov": {
        "password_hash": hash_password("teach2026"),
        "role": "teacher", "full_name": "Сидоров Илья Игоревич",
        "student_id": None, "teacher_id": 3, "is_active": True, "last_password_change": "2026-03-15",
    },
    # ── Администратор ──
    "admin_demo": {
        "password_hash": hash_password("admin2026"),
        "role": "administrator", "full_name": "Новикова Наталья Михайловна",
        "student_id": None, "teacher_id": None, "is_active": True, "last_password_change": "2026-04-12",
    },
    # ── Бухгалтер ──
    "accountant_demo": {
        "password_hash": hash_password("acc2026"),
        "role": "accountant", "full_name": "Громова Светлана Ивановна",
        "student_id": None, "teacher_id": None, "is_active": True, "last_password_change": "2026-04-01",
    },
}

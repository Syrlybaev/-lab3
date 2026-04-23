from __future__ import annotations

# Типы финансовых операций
FINANCE_TYPES: dict[str, str] = {
    "tuition":          "Оплата обучения",
    "dorm":             "Оплата общежития",
    "scholarship_base": "Академическая стипендия",
    "scholarship_high": "Повышенная стипендия",
    "social":           "Социальная выплата",
}

# sign: +1 → начисление студенту (доход), -1 → платёж студента (расход)
FINANCE_RECORDS: list[dict] = [
    # Смирнова Елена (id=1)
    {"id":  1, "student_id":  1, "op_type": "tuition",          "amount": 95000.0, "period": "2026 весна", "date": "2026-02-10", "status": "Оплачено",  "sign": -1, "comment": "Оплата обучения 2026 весна"},
    {"id":  2, "student_id":  1, "op_type": "dorm",             "amount": 3500.0,  "period": "2026-02",   "date": "2026-02-05", "status": "Оплачено",  "sign": -1, "comment": "Общежитие февраль"},
    {"id":  3, "student_id":  1, "op_type": "dorm",             "amount": 3500.0,  "period": "2026-03",   "date": "2026-03-04", "status": "Оплачено",  "sign": -1, "comment": "Общежитие март"},
    {"id":  4, "student_id":  1, "op_type": "dorm",             "amount": 3500.0,  "period": "2026-04",   "date": "2026-04-03", "status": "Ожидает",   "sign": -1, "comment": "Общежитие апрель"},
    {"id":  5, "student_id":  1, "op_type": "scholarship_base", "amount": 5000.0,  "period": "2026-02",   "date": "2026-02-15", "status": "Выплачено", "sign": +1, "comment": "Академическая стипендия февраль"},
    {"id":  6, "student_id":  1, "op_type": "scholarship_base", "amount": 5000.0,  "period": "2026-03",   "date": "2026-03-15", "status": "Выплачено", "sign": +1, "comment": "Академическая стипендия март"},
    {"id":  7, "student_id":  1, "op_type": "scholarship_high", "amount": 8500.0,  "period": "2026-02",   "date": "2026-02-15", "status": "Выплачено", "sign": +1, "comment": "Повышенная стипендия"},

    # Кузнецов Артём (id=2)
    {"id":  8, "student_id":  2, "op_type": "tuition",          "amount": 110000.0,"period": "2026 весна", "date": "2026-02-12", "status": "Оплачено",  "sign": -1, "comment": "Оплата обучения 2026 весна"},
    {"id":  9, "student_id":  2, "op_type": "scholarship_base", "amount": 5000.0,  "period": "2026-02",   "date": "2026-02-15", "status": "Выплачено", "sign": +1, "comment": "Стипендия февраль"},
    {"id": 10, "student_id":  2, "op_type": "social",           "amount": 3000.0,  "period": "2026-02",   "date": "2026-02-20", "status": "Выплачено", "sign": +1, "comment": "Социальная выплата"},

    # Орлова Мария (id=7)
    {"id": 11, "student_id":  7, "op_type": "tuition",          "amount": 95000.0, "period": "2026 весна", "date": "2026-02-08", "status": "Оплачено",  "sign": -1, "comment": "Оплата обучения 2026 весна"},
    {"id": 12, "student_id":  7, "op_type": "scholarship_high", "amount": 8500.0,  "period": "2026-03",   "date": "2026-03-15", "status": "Выплачено", "sign": +1, "comment": "Повышенная стипендия март"},

    # Фёдоров Илья (id=8) — должник
    {"id": 13, "student_id":  8, "op_type": "tuition",          "amount": 110000.0,"period": "2026 весна", "date": "2026-04-23", "status": "Не оплачено","sign": -1, "comment": "Обучение не оплачено"},
    {"id": 14, "student_id":  8, "op_type": "dorm",             "amount": 3500.0,  "period": "2026-03",   "date": "2026-04-23", "status": "Не оплачено","sign": -1, "comment": "Общежитие март не оплачено"},

    # Попов Александр (id=12)
    {"id": 15, "student_id": 12, "op_type": "tuition",          "amount": 95000.0, "period": "2026 весна", "date": "2026-02-14", "status": "Оплачено",  "sign": -1, "comment": "Оплата обучения"},
    {"id": 16, "student_id": 12, "op_type": "scholarship_base", "amount": 5000.0,  "period": "2026-03",   "date": "2026-03-15", "status": "Выплачено", "sign": +1, "comment": "Стипендия март"},

    # Гусев Роман (id=16) — должник
    {"id": 17, "student_id": 16, "op_type": "tuition",          "amount": 110000.0,"period": "2026 весна", "date": "2026-04-23", "status": "Не оплачено","sign": -1, "comment": "Обучение не оплачено"},
]

import sqlite3

db_path = "c:\\Fvus\\ISIT\\lab3_my\\-lab3\\dekanat.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all teachers
cursor.execute("SELECT id FROM teachers")
teachers = cursor.fetchall()

# Add salary records for each teacher
salaries = [
    {'teacher_id': t[0], 'op_type': 'salary', 'amount': 85000.0, 
     'period': '2026-04', 'date': '2026-04-05', 'status': 'Выплачено', 'sign': 1, 
     'comment': 'Зарплата апрель 2026'}
    for t in teachers
]

# Add March salary too
salaries += [
    {'teacher_id': t[0], 'op_type': 'salary', 'amount': 85000.0, 
     'period': '2026-03', 'date': '2026-03-05', 'status': 'Выплачено', 'sign': 1, 
     'comment': 'Зарплата март 2026'}
    for t in teachers
]

for s in salaries:
    cursor.execute("""
        INSERT INTO finance (student_id, teacher_id, op_type, amount, period, date, status, sign, comment)
        VALUES (NULL, :teacher_id, :op_type, :amount, :period, :date, :status, :sign, :comment)
    """, s)

conn.commit()
conn.close()
print(f"Added {len(salaries)} salary records for {len(teachers)} teachers.")

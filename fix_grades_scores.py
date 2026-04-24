import sqlite3
import random

db_path = "c:\\Fvus\\ISIT\\lab3_my\\-lab3\\dekanat.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Получаем все оценки
cursor.execute("SELECT id, control_type, credit, exam FROM grades")
rows = cursor.fetchall()

for row_id, control_type, credit, exam in rows:
    new_credit = credit
    new_exam = exam
    
    # Генерируем случайный балл от 35 до 52 для реалистичности
    score = str(random.randint(35, 52))
    
    if credit == 'Зачет':
        new_credit = score
    if exam == 'Экзамен':
        new_exam = score
        
    cursor.execute("UPDATE grades SET credit = ?, exam = ? WHERE id = ?", (new_credit, new_exam, row_id))

conn.commit()
conn.close()
print("Все текстовые отметки 'Зачет' и 'Экзамен' заменены на числовые баллы.")

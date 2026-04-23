import sqlite3
from data_sample import USERS, STUDENTS, TEACHERS, SCHEDULE_DATA, GRADE_RECORDS, FINANCE_RECORDS
from services.database import DatabaseService

def migrate():
    db = DatabaseService()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Очищаем перед миграцией (на всякий случай)
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM teachers")
        cursor.execute("DELETE FROM teacher_subjects")
        cursor.execute("DELETE FROM schedule")
        cursor.execute("DELETE FROM grades")
        cursor.execute("DELETE FROM finance")

        # Перенос пользователей
        for login, info in USERS.items():
            cursor.execute("""
                INSERT INTO users (login, password_hash, role, full_name, student_id, teacher_id, is_active, last_password_change)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (login, info['password_hash'], info['role'], info['full_name'], 
                  info['student_id'], info['teacher_id'], info['is_active'], info['last_password_change']))

        # Перенос студентов
        for s in STUDENTS:
            cursor.execute("""
                INSERT INTO students (id, full_name, study_group, record_book, course, program, study_form, funding, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (s['id'], s['full_name'], s['group'], s['record_book'], 
                  s['course'], s['program'], s['study_form'], s['funding'], s['status']))

        # Перенос преподавателей
        for t in TEACHERS:
            cursor.execute("""
                INSERT INTO teachers (id, full_name, department, position, degree, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (t['id'], t['full_name'], t['department'], t['position'], t['degree'], t['email'], t['phone']))
            
            for sub in t['subjects']:
                cursor.execute("INSERT INTO teacher_subjects (teacher_id, subject) VALUES (?, ?)", (t['id'], sub))

        # Перенос расписания
        for s in SCHEDULE_DATA:
            cursor.execute("""
                INSERT INTO schedule (day, pair, time, study_group, subject, teacher_id, lesson_type, format, room, date_start, date_end)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (s['day'], s['pair'], s['time'], s['group'], s['subject'], 
                  s['teacher_id'], s['lesson_type'], s['format'], s['room'], s.get('date_start'), s.get('date_end')))

        # Перенос оценок
        for g in GRADE_RECORDS:
            credit = 'Зачет' if g['control_type'] == 'Зачет' else '-'
            exam = 'Экзамен' if g['control_type'] == 'Экзамен' else '-'
            cursor.execute("""
                INSERT INTO grades (id, student_id, teacher_id, subject, semester, control_type, m1, m2, credit, exam, coefficient, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (g['id'], g['student_id'], g['teacher_id'], g['subject'], 
                  g['semester'], g['control_type'], g['m1'], g['m2'], credit, exam, g.get('coefficient', 1.0), g['status']))

        # Перенос финансов
        for f in FINANCE_RECORDS:
            cursor.execute("""
                INSERT INTO finance (id, student_id, op_type, amount, period, date, status, sign, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f['id'], f['student_id'], f['op_type'], f['amount'], 
                  f['period'], f['date'], f['status'], f['sign'], f['comment']))

        conn.commit()
    print("Миграция данных в SQLite завершена успешно!")

if __name__ == "__main__":
    migrate()

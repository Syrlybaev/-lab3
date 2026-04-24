import sqlite3
import os

class DatabaseService:
    def __init__(self, db_path="dekanat.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    login TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    student_id INTEGER,
                    teacher_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    last_password_change TEXT
                )
            """)

            # Таблица студентов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    study_group TEXT NOT NULL,
                    record_book TEXT UNIQUE,
                    course INTEGER,
                    program TEXT,
                    study_form TEXT,
                    funding TEXT,
                    status TEXT
                )
            """)

            # Таблица преподавателей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    department TEXT,
                    position TEXT,
                    degree TEXT,
                    contacts TEXT
                )
            """)
            
            # Таблица дисциплин преподавателей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher_subjects (
                    teacher_id INTEGER,
                    subject TEXT,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
                )
            """)

            # Таблица расписания
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT NOT NULL,
                    pair INTEGER NOT NULL,
                    time TEXT,
                    study_group TEXT,
                    subject TEXT,
                    teacher_id INTEGER,
                    lesson_type TEXT,
                    format TEXT,
                    room TEXT,
                    date_start TEXT,
                    date_end TEXT,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
                )
            """)

            # Таблица оценок
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    teacher_id INTEGER,
                    subject TEXT,
                    semester TEXT,
                    control_type TEXT,
                    m1 INTEGER DEFAULT 0,
                    m2 INTEGER DEFAULT 0,
                    credit TEXT DEFAULT '-',
                    exam TEXT DEFAULT '-',
                    coefficient REAL DEFAULT 1.0,
                    status TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
                )
            """)
            
            # Таблица аудита оценок
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grade_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    grade_id INTEGER,
                    changed_by TEXT,
                    old_m1 INTEGER,
                    old_m2 INTEGER,
                    new_m1 INTEGER,
                    new_m2 INTEGER,
                    changed_at TEXT,
                    comment TEXT,
                    FOREIGN KEY(grade_id) REFERENCES grades(id)
                )
            """)

            # Таблица финансов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    teacher_id INTEGER,
                    op_type TEXT,
                    amount REAL,
                    period TEXT,
                    date TEXT,
                    status TEXT,
                    sign INTEGER,
                    comment TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
                )
            """)
            
            conn.commit()

    # --- Методы для работы с данными (примеры) ---

    def get_users(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM users").fetchall()]

    def get_user_by_login(self, login):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            res = conn.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
            return dict(res) if res else None

    def get_students(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM students").fetchall()]

    def get_teachers(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            teachers = [dict(row) for row in conn.execute("SELECT * FROM teachers").fetchall()]
            for t in teachers:
                subs = conn.execute("SELECT subject FROM teacher_subjects WHERE teacher_id = ?", (t['id'],)).fetchall()
                t['subjects'] = [s[0] for s in subs]
            return teachers

    def get_schedule(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT s.*, t.full_name as teacher_name 
                FROM schedule s
                LEFT JOIN teachers t ON s.teacher_id = t.id
            """
            return [dict(row) for row in conn.execute(query).fetchall()]

    def get_grades(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM grades").fetchall()]

    def get_finance(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM finance").fetchall()]

    # Методы обновления (пример для оценок)
    def update_grade(self, grade_id, m1, m2, credit, exam, status, changed_by, comment=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Берем старые данные для аудита
            old = cursor.execute("SELECT m1, m2 FROM grades WHERE id = ?", (grade_id,)).fetchone()
            if not old: return False
            
            cursor.execute("""
                UPDATE grades 
                SET m1 = ?, m2 = ?, credit = ?, exam = ?, status = ? 
                WHERE id = ?
            """, (m1, m2, credit, exam, status, grade_id))
            
            cursor.execute("""
                INSERT INTO grade_audit (grade_id, changed_by, old_m1, old_m2, new_m1, new_m2, changed_at, comment)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
            """, (grade_id, changed_by, old[0], old[1], m1, m2, comment))
            
            conn.commit()
            return True

    def delete_grade(self, grade_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
            conn.commit()
            return True

    def add_grade(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO grades (student_id, teacher_id, subject, semester, control_type, m1, m2, credit, exam, coefficient, status)
                VALUES (:student_id, :teacher_id, :subject, :semester, :control_type, :m1, :m2, :credit, :exam, :coefficient, :status)
            """, data)
            conn.commit()
            return cursor.lastrowid

    def add_student(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (full_name, study_group, record_book, course, program, study_form, funding, status)
                VALUES (:full_name, :study_group, :record_book, :course, :program, :study_form, :funding, :status)
            """, data)
            conn.commit()
            return cursor.lastrowid

    def update_student(self, student_id, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE students SET 
                full_name = :full_name, study_group = :study_group, record_book = :record_book, 
                course = :course, program = :program, study_form = :study_form, 
                funding = :funding, status = :status
                WHERE id = :id
            """, {**data, 'id': student_id})
            conn.commit()
            return True

    def delete_student(self, student_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            return True

    # --- Schedule CRUD ---
    def add_schedule_item(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO schedule (day, pair, time, study_group, subject, teacher_id, lesson_type, format, room, date_start, date_end)
                VALUES (:day, :pair, :time, :study_group, :subject, :teacher_id, :lesson_type, :format, :room, :date_start, :date_end)
            """, data)
            conn.commit()
            return cursor.lastrowid

    def update_schedule_item(self, item_id, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE schedule SET 
                day = :day, pair = :pair, time = :time, study_group = :study_group, 
                subject = :subject, teacher_id = :teacher_id, lesson_type = :lesson_type, 
                format = :format, room = :room, date_start = :date_start, date_end = :date_end
                WHERE id = :id
            """, {**data, 'id': item_id})
            conn.commit()
            return True

    def delete_schedule_item(self, item_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM schedule WHERE id = ?", (item_id,))
            conn.commit()
            return True

    # --- User CRUD ---
    def add_user(self, data):
        from services.utils import hash_password
        with self.get_connection() as conn:
            cursor = conn.cursor()
            data['password_hash'] = hash_password(data.get('password', '12345'))
            cursor.execute("""
                INSERT INTO users (login, password_hash, role, full_name, student_id, teacher_id)
                VALUES (:login, :password_hash, :role, :full_name, :student_id, :teacher_id)
            """, data)
            conn.commit()
            return cursor.lastrowid

    def update_user(self, user_login, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET 
                role = :role, full_name = :full_name, 
                student_id = :student_id, teacher_id = :teacher_id
                WHERE login = :login
            """, {**data, 'login': user_login})
            conn.commit()
            return True

    def delete_user(self, user_login):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM users WHERE login = ?", (user_login,))
            conn.commit()
            return True

    # --- Finance CRUD ---
    def add_finance_operation(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO finance (student_id, teacher_id, op_type, amount, period, date, status, sign, comment)
                VALUES (:student_id, :teacher_id, :op_type, :amount, :period, :date, :status, :sign, :comment)
            """, data)
            conn.commit()
            return cursor.lastrowid

    def update_finance_operation(self, op_id, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE finance SET 
                student_id = :student_id, teacher_id = :teacher_id, op_type = :op_type, amount = :amount, 
                period = :period, date = :date, status = :status, sign = :sign, comment = :comment
                WHERE id = :id
            """, {**data, 'id': op_id})
            conn.commit()
            return True

    def delete_finance_operation(self, op_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM finance WHERE id = ?", (op_id,))
            conn.commit()
            return True

    # --- Teacher CRUD ---
    def add_teacher(self, data, subjects=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teachers (full_name, department, position, degree, contacts)
                VALUES (:full_name, :department, :position, :degree, :contacts)
            """, data)
            teacher_id = cursor.lastrowid
            if subjects:
                for sub in subjects:
                    cursor.execute("INSERT INTO teacher_subjects (teacher_id, subject) VALUES (?, ?)", (teacher_id, sub))
            conn.commit()
            return teacher_id

    def update_teacher(self, teacher_id, data, subjects=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE teachers SET 
                full_name = :full_name, department = :department, 
                position = :position, degree = :degree, contacts = :contacts
                WHERE id = :id
            """, {**data, 'id': teacher_id})
            
            if subjects is not None:
                cursor.execute("DELETE FROM teacher_subjects WHERE teacher_id = ?", (teacher_id,))
                for sub in subjects:
                    cursor.execute("INSERT INTO teacher_subjects (teacher_id, subject) VALUES (?, ?)", (teacher_id, sub))
            
            conn.commit()
            return True

    def delete_teacher(self, teacher_id):
        with self.get_connection() as conn:
            # First delete subjects
            conn.execute("DELETE FROM teacher_subjects WHERE teacher_id = ?", (teacher_id,))
            conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
            conn.commit()
            return True

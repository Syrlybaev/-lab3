# Полный код проекта: Виртуальный Деканат

## app.py
```python
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from services.database import DatabaseService
from services.auth import AuthService
from services.rbac import RBACService
from services.utils import ROLE_LABELS, grade_label, format_name_initials
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = DatabaseService()
auth = AuthService()
rbac = RBACService()

# --- Контекстные процессоры ---
@app.context_processor
def inject_globals():
    user = None
    if 'user' in session:
        user = session['user']
    return dict(
        role_labels=ROLE_LABELS,
        current_user=user,
        rbac=rbac,
        format_name=format_name_initials
    )

# --- Middleware для проверки авторизации ---
@app.before_request
def require_login():
    exempt_routes = ['login', 'static']
    if request.endpoint not in exempt_routes and 'user' not in session:
        return redirect(url_for('login'))

# --- Роуты ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_val = request.form.get('login', '').strip()
        password_val = request.form.get('password', '').strip()
        
        user = auth.authenticate_password(login_val, password_val)
        if user:
            # Преобразуем SessionUser dataclass в словарь для сессии
            session['user'] = {
                'login': user.login,
                'role': user.role,
                'full_name': user.full_name,
                'student_id': user.student_id,
                'teacher_id': user.teacher_id
            }
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
def dashboard():
    user = session['user']
    # Доп. данные для студента
    student_info = None
    if user['role'] == 'student' and user['student_id']:
        students = db.get_students()
        student_info = next((s for s in students if s['id'] == user['student_id']), None)
        
    return render_template('dashboard.html', student=student_info)

@app.route('/schedule')
def schedule():
    user = session['user']
    all_schedule = db.get_schedule()
    all_teachers = db.get_teachers()
    all_groups = sorted(list(set(s['study_group'] for s in db.get_students())))

    # Параметры фильтрации
    selected_group = request.args.get('group')
    selected_teacher = request.args.get('teacher_id')

    # Применение фильтров
    if selected_group and selected_group != 'Все':
        all_schedule = [s for s in all_schedule if s['study_group'] == selected_group]
    
    if selected_teacher and selected_teacher != 'Все':
        all_schedule = [s for s in all_schedule if str(s['teacher_id']) == selected_teacher]
        
    if not selected_group and not selected_teacher:
            if user['role'] == 'student' and user['student_id']:
                student = next((s for s in db.get_students() if s['id'] == user['student_id']), None)
                if student:
                    all_schedule = [s for s in all_schedule if s['study_group'] == student['study_group']]
                    selected_group = student['study_group']
            elif user['role'] == 'teacher' and user['teacher_id']:
                all_schedule = [s for s in all_schedule if s['teacher_id'] == user['teacher_id']]
                selected_teacher = str(user['teacher_id'])

    # Сортировка по дням недели
    from services.utils import DAY_ORDER
    all_schedule.sort(key=lambda x: (DAY_ORDER.get(x['day'], 9), x['pair']))
    
    # Группировка по дням
    schedule_by_day = {}
    for item in all_schedule:
        day = item['day']
        if day not in schedule_by_day:
            schedule_by_day[day] = []
        schedule_by_day[day].append(item)
        
    return render_template('schedule.html', 
                           schedule_data=schedule_by_day, 
                           day_order=DAY_ORDER,
                           groups=all_groups,
                           teachers=all_teachers,
                           selected_group=selected_group,
                           selected_teacher=selected_teacher)

@app.route('/schedule/add', methods=['POST'])
def add_schedule():
    if not rbac.check(session['user']['role'], 'schedule', 'manage').allowed:
        return "Доступ запрещен", 403
    
    data = {
        'day': request.form.get('day'),
        'pair': int(request.form.get('pair')),
        'time': request.form.get('time'),
        'study_group': request.form.get('study_group'),
        'subject': request.form.get('subject'),
        'teacher_id': int(request.form.get('teacher_id')),
        'lesson_type': request.form.get('lesson_type', 'Лекция'),
        'format': request.form.get('format', 'Очная'),
        'room': request.form.get('room'),
        'date_start': '2026-02-09',
        'date_end': '2026-06-20'
    }
    
    if db.add_schedule_item(data):
        flash('Занятие добавлено', 'success')
    return redirect(url_for('schedule'))

@app.route('/schedule/edit/<int:item_id>', methods=['POST'])
def edit_schedule(item_id):
    if not rbac.check(session['user']['role'], 'schedule', 'manage').allowed:
        return "Доступ запрещен", 403
    
    data = {
        'day': request.form.get('day'),
        'pair': int(request.form.get('pair')),
        'time': request.form.get('time'),
        'study_group': request.form.get('study_group'),
        'subject': request.form.get('subject'),
        'teacher_id': int(request.form.get('teacher_id')),
        'lesson_type': request.form.get('lesson_type'),
        'format': request.form.get('format'),
        'room': request.form.get('room'),
        'date_start': request.form.get('date_start'),
        'date_end': request.form.get('date_end')
    }
    
    if db.update_schedule_item(item_id, data):
        flash('Занятие обновлено', 'success')
    return redirect(url_for('schedule'))

@app.route('/schedule/delete/<int:item_id>', methods=['POST'])
def delete_schedule(item_id):
    if not rbac.check(session['user']['role'], 'schedule', 'manage').allowed:
        return "Доступ запрещен", 403
    
    if db.delete_schedule_item(item_id):
        flash('Занятие удалено', 'success')
    return redirect(url_for('schedule'))

@app.route('/grades')
def grades():
    user = session['user']
    all_grades = db.get_grades()
    all_students = db.get_students()
    students_dict = {s['id']: s for s in all_students}
    teachers_dict = {t['id']: t for t in db.get_teachers()}
    all_semesters = sorted(list(set(g.get('semester', '-') for g in all_grades)), reverse=True)
    selected_semester = request.args.get('semester')
    if not selected_semester and all_semesters:
        selected_semester = all_semesters[0]
    
    selected_group = request.args.get('group')
    
    # Сначала фильтруем по семестру
    if selected_semester:
        all_grades = [g for g in all_grades if g.get('semester') == selected_semester]

    # Фильтрация по роли
    if user['role'] == 'student':
        all_grades = [g for g in all_grades if g['student_id'] == user['student_id']]
    elif user['role'] == 'teacher':
        all_grades = [g for g in all_grades if g['teacher_id'] == user['teacher_id']]
        
    # Фильтрация по группе (если выбрана)
    if selected_group and selected_group != 'Все':
        all_grades = [g for g in all_grades if students_dict.get(g['student_id'], {}).get('study_group') == selected_group]
        
    # Данные для модалки добавления
    teacher_subjects = []
    if user['role'] == 'teacher' and user['teacher_id']:
        t = next((t for t in db.get_teachers() if t['id'] == user['teacher_id']), None)
        if t: teacher_subjects = t.get('subjects', [])
    elif user['role'] == 'administrator':
        # Админ может видеть все дисциплины всех учителей
        all_t = db.get_teachers()
        for t in all_t: teacher_subjects.extend(t.get('subjects', []))
        teacher_subjects = sorted(list(set(teacher_subjects)))

    groups = sorted(list(set(s['study_group'] for s in all_students)))

    return render_template('grades.html', 
                           grades=all_grades, 
                           students=students_dict, 
                           all_students=all_students,
                           teacher_subjects=teacher_subjects,
                           teachers=teachers_dict, 
                           groups=groups,
                           selected_group=selected_group,
                           all_semesters=all_semesters,
                           selected_semester=selected_semester,
                           grade_label=grade_label)

@app.route('/grades/update', methods=['POST'])
def update_grade():
    user = session['user']
    if user['role'] not in ['teacher', 'administrator']:
        return "Доступ запрещен", 403
    
    grade_id = request.form.get('grade_id')
    m1 = int(request.form.get('m1', 0))
    m2 = int(request.form.get('m2', 0))
    credit = request.form.get('credit', '-')
    exam = request.form.get('exam', '-')
    status = request.form.get('status', 'Подтверждена')
    
    if grade_id:
        # Редактирование
        success = db.update_grade(grade_id, m1, m2, credit, exam, status, user['full_name'])
        msg = 'Оценка успешно обновлена'
    else:
        # Добавление новой
        data = {
            'student_id': int(request.form.get('student_id')),
            'teacher_id': user['teacher_id'] or 1, # Временный фикс для админа
            'subject': request.form.get('subject'),
            'semester': '2026 весна',
            'control_type': 'Экзамен' if exam != '-' else 'Зачет',
            'm1': m1,
            'm2': m2,
            'credit': credit,
            'exam': exam,
            'coefficient': float(request.form.get('coefficient', 1.0)),
            'status': status
        }
        success = db.add_grade(data)
        msg = 'Новая оценка успешно выставлена'
        
    if success:
        flash(msg, 'success')
    else:
        flash('Ошибка при сохранении оценки', 'error')
        
    current_group = request.form.get('current_group')
    if current_group and current_group != 'None' and current_group != '':
        return redirect(url_for('grades', group=current_group))
    return redirect(url_for('grades'))

@app.route('/grades/delete/<int:grade_id>', methods=['POST'])
def delete_grade(grade_id):
    user = session['user']
    if user['role'] not in ['teacher', 'administrator']:
        return "Доступ запрещен", 403
        
    if db.delete_grade(grade_id):
        flash('Запись удалена', 'success')
    return redirect(url_for('grades'))

@app.route('/finance')
def finance():
    user = session['user']
    all_finance = db.get_finance()
    students = {s['id']: s for s in db.get_students()}
    teachers = {t['id']: t for t in db.get_teachers()}
    
    FINANCE_TYPES = {
        "tuition":          "Оплата обучения",
        "dorm":             "Оплата общежития",
        "scholarship_base": "Академическая стипендия",
        "scholarship_high": "Повышенная стипендия",
        "social":           "Социальная выплата",
        "salary":           "Зарплата преподавателя",
        "bonus":            "Премия"
    }
    
    if user['role'] == 'student':
        all_finance = [f for f in all_finance if f.get('student_id') == user['student_id']]
    elif user['role'] == 'teacher':
        all_finance = [f for f in all_finance if f.get('teacher_id') == user['teacher_id']]
        
    for f in all_finance:
        f['op_type'] = FINANCE_TYPES.get(f['op_type'], f['op_type'])
        
    return render_template('finance.html', finance_data=all_finance, students=students, teachers=teachers)

@app.route('/students')
def students():
    if not rbac.check(session['user']['role'], 'students', 'view').allowed:
        return "Доступ запрещен", 403
    return render_template('students.html', students=db.get_students())

@app.route('/students/add', methods=['POST'])
def add_student():
    if not rbac.check(session['user']['role'], 'students', 'manage').allowed:
        return "Доступ запрещен", 403
        
    data = {
        'full_name': request.form.get('full_name'),
        'study_group': request.form.get('study_group'),
        'record_book': request.form.get('record_book'),
        'course': int(request.form.get('course', 1)),
        'program': request.form.get('program'),
        'study_form': request.form.get('study_form', 'Очная'),
        'funding': request.form.get('funding', 'Бюджет'),
        'status': 'Активен'
    }
    
    success = db.add_student(data)
    if success:
        flash('Студент успешно добавлен', 'success')
    else:
        flash('Ошибка при добавлении студента', 'error')
        
    return redirect(url_for('students'))

@app.route('/students/edit/<int:student_id>', methods=['POST'])
def edit_student(student_id):
    if not rbac.check(session['user']['role'], 'students', 'manage').allowed:
        return "Доступ запрещен", 403
        
    data = {
        'full_name': request.form.get('full_name'),
        'study_group': request.form.get('study_group'),
        'record_book': request.form.get('record_book'),
        'course': int(request.form.get('course', 1)),
        'program': request.form.get('program'),
        'study_form': request.form.get('study_form', 'Очная'),
        'funding': request.form.get('funding', 'Бюджет'),
        'status': request.form.get('status', 'Активен')
    }
    
    if db.update_student(student_id, data):
        flash('Данные студента обновлены', 'success')
    else:
        flash('Ошибка при обновлении', 'error')
    return redirect(url_for('students'))

@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if not rbac.check(session['user']['role'], 'students', 'manage').allowed:
        return "Доступ запрещен", 403
        
    if db.delete_student(student_id):
        flash('Студент удален', 'success')
    return redirect(url_for('students'))

@app.route('/teachers')
def teachers():
    if not rbac.check(session['user']['role'], 'teachers', 'view').allowed:
        return "Доступ запрещен", 403
    return render_template('teachers.html', teachers=db.get_teachers())

@app.route('/teachers/add', methods=['POST'])
def add_teacher():
    if not rbac.check(session['user']['role'], 'teachers', 'manage').allowed:
        return "Доступ запрещен", 403
    data = {
        'full_name': request.form.get('full_name'),
        'department': request.form.get('department'),
        'position': request.form.get('position'),
        'degree': request.form.get('degree'),
        'contacts': request.form.get('contacts')
    }
    subs_raw = request.form.get('subjects', '')
    subjects = [s.strip() for s in subs_raw.split(',') if s.strip()]
    if db.add_teacher(data, subjects):
        flash('Преподаватель добавлен', 'success')
    return redirect(url_for('teachers'))

@app.route('/teachers/edit/<int:teacher_id>', methods=['POST'])
def edit_teacher(teacher_id):
    if not rbac.check(session['user']['role'], 'teachers', 'manage').allowed:
        return "Доступ запрещен", 403
    data = {
        'full_name': request.form.get('full_name'),
        'department': request.form.get('department'),
        'position': request.form.get('position'),
        'degree': request.form.get('degree'),
        'contacts': request.form.get('contacts')
    }
    subs_raw = request.form.get('subjects', '')
    subjects = [s.strip() for s in subs_raw.split(',') if s.strip()]
    if db.update_teacher(teacher_id, data, subjects):
        flash('Данные обновлены', 'success')
    return redirect(url_for('teachers'))

@app.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    if not rbac.check(session['user']['role'], 'teachers', 'manage').allowed:
        return "Доступ запрещен", 403
    if db.delete_teacher(teacher_id):
        flash('Преподаватель удален', 'success')
    return redirect(url_for('teachers'))

@app.route('/users')
def users():
    if not rbac.check(session['user']['role'], 'users', 'view').allowed:
        return "Доступ запрещен", 403
    return render_template('users.html', users=db.get_users())

@app.route('/users/add', methods=['POST'])
def add_user():
    if not rbac.check(session['user']['role'], 'users', 'manage').allowed:
        return "Доступ запрещен", 403
    data = {
        'login': request.form.get('login'),
        'password': request.form.get('password'),
        'role': request.form.get('role'),
        'full_name': request.form.get('full_name'),
        'student_id': int(request.form.get('student_id')) if request.form.get('student_id') else None,
        'teacher_id': int(request.form.get('teacher_id')) if request.form.get('teacher_id') else None
    }
    if db.add_user(data):
        flash('Пользователь создан', 'success')
    return redirect(url_for('users'))

@app.route('/users/edit/<login>', methods=['POST'])
def edit_user(login):
    if not rbac.check(session['user']['role'], 'users', 'manage').allowed:
        return "Доступ запрещен", 403
    data = {
        'role': request.form.get('role'),
        'full_name': request.form.get('full_name'),
        'student_id': int(request.form.get('student_id')) if request.form.get('student_id') else None,
        'teacher_id': int(request.form.get('teacher_id')) if request.form.get('teacher_id') else None
    }
    if db.update_user(login, data):
        flash('Данные обновлены', 'success')
    return redirect(url_for('users'))

@app.route('/users/delete/<login>', methods=['POST'])
def delete_user(login):
    if not rbac.check(session['user']['role'], 'users', 'manage').allowed:
        return "Доступ запрещен", 403
    if db.delete_user(login):
        flash('Пользователь удален', 'success')
    return redirect(url_for('users'))

# --- Finance Routes ---

@app.route('/finance/add', methods=['POST'])
def add_finance():
    if session['user']['role'] not in ['administrator', 'accountant']:
        return "Доступ запрещен", 403
    student_id_raw = request.form.get('student_id', '0')
    student_id_val = int(student_id_raw) if student_id_raw else 0
    op_type = request.form.get('type')
    amount = float(request.form.get('amount'))
    
    data = {
        'student_id': student_id_val if student_id_val > 0 else None,
        'teacher_id': None, # Simplification, admin can only add to students from UI right now
        'op_type': op_type,
        'amount': amount,
        'period': '2026-04',
        'date': request.form.get('date', '2026-04-23'),
        'status': request.form.get('status', 'Завершено'),
        'sign': -1 if op_type == 'Штраф' else 1,
        'comment': request.form.get('description')
    }
    if db.add_finance_operation(data):
        flash('Операция добавлена', 'success')
    return redirect(url_for('finance'))

@app.route('/finance/delete/<int:op_id>', methods=['POST'])
def delete_finance(op_id):
    if session['user']['role'] not in ['administrator', 'accountant']:
        return "Доступ запрещен", 403
    if db.delete_finance_operation(op_id):
        flash('Операция удалена', 'success')
    return redirect(url_for('finance'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

```

## requirements.txt
```txt
Flask==3.0.0

```

## README.md
```md
# Виртуальный Деканат (Virtual Deanery)

Информационная система для управления учебным процессом, разработанная в рамках Лабораторной работы №3 по дисциплине "Информационные системы и технологии".

## 🚀 Особенности
- **Аутентификация и авторизация**: Вход по логину/паролю с разграничением прав доступа (RBAC).
- **Роли пользователей**:
  - **Студент**: Просмотр оценок, расписания и финансовых операций.
  - **Преподаватель**: Управление оценками своих студентов, просмотр расписания.
  - **Администратор**: Полный доступ к управлению студентами, преподавателями, пользователями и расписанием.
- **Модули**:
  - Оценки (учет баллов M1, M2, зачетов и экзаменов).
  - Расписание (фильтрация по группам и преподавателям).
  - Финансы (учет оплат и штрафов).
  - Управление персоналом (студенты, преподаватели, пользователи).

## 🛠 Технологии
- **Backend**: Python 3.10+, Flask
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla CSS3 (современный адаптивный дизайн), Lucide Icons

## 📋 Инструкция по запуску

### 1. Подготовка окружения
Убедитесь, что у вас установлен Python. Рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для Linux/macOS:
source venv/bin/activate
```

### 2. Установка зависимостей
Установите все необходимые модули одной командой:

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных
Если файл `dekanat.db` отсутствует или пуст, выполните скрипт миграции для наполнения базы демонстрационными данными:

```bash
python migrate_to_db.py
```

### 4. Запуск приложения
Запустите основной файл приложения:

```bash
python app.py
```

После этого приложение будет доступно по адресу: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🔑 Демо-данные для входа

| Роль | Логин | Пароль |
| :--- | :--- | :--- |
| **Администратор** | `admin_demo` | `admin2026` |
| **Преподаватель** | `teacher_demo` | `teach2026` |
| **Студент** | `student_demo` | `stud2026` |

---
*Разработано для образовательных целей.*

```

## migrate_to_db.py
```python
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
            credit = '40' if g['control_type'] == 'Зачет' else '-'
            exam = '40' if g['control_type'] == 'Экзамен' else '-'
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

```

## services/auth.py
```python
from __future__ import annotations

from dataclasses import dataclass

from services.database import DatabaseService
from services.utils import ROLE_LABELS, hash_password


@dataclass(frozen=True)
class SessionUser:
    login: str
    role: str
    full_name: str
    student_id: int | None
    teacher_id: int | None


class AuthService:
    def __init__(self) -> None:
        self.db = DatabaseService()

    def authenticate_password(self, login: str, password: str) -> SessionUser | None:
        user_data = self.db.get_user_by_login(login)
        if not user_data or not user_data['is_active']:
            return None
        
        if user_data['password_hash'] == hash_password(password):
            return SessionUser(
                login=user_data['login'],
                role=user_data['role'],
                full_name=user_data['full_name'],
                student_id=user_data['student_id'],
                teacher_id=user_data['teacher_id']
            )
        return None

    @staticmethod
    def role_as_text(role: str) -> str:
        return ROLE_LABELS.get(role, role)

```

## services/database.py
```python
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

```

## services/rbac.py
```python
from __future__ import annotations

from dataclasses import dataclass

from services.utils import ROLE_LABELS

ACL: dict[str, dict[str, set[str]]] = {
    "schedule": {
        "view":   {"student", "teacher", "administrator"},
        "edit":   {"administrator"},
        "manage": {"administrator"},
    },
    "grades": {
        "view_own": {"student"},
        "view_all": {"teacher", "administrator", "accountant"},
        "edit":     {"teacher", "administrator"},
    },
    "students": {
        "view":   {"teacher", "administrator"},
        "manage": {"administrator"},
    },
    "teachers": {
        "view":   {"administrator"},
        "manage": {"administrator"},
    },
    "users": {
        "view":   {"administrator"},
        "manage": {"administrator"},
    },
    "finance": {
        "view_own": {"student", "teacher"},
        "view_all": {"accountant", "administrator"},
        "manage":   {"accountant", "administrator"},
    },
}

MENU_SECTIONS: list[dict[str, str]] = [
    {"resource": "schedule", "title": "Расписание"},
    {"resource": "grades",   "title": "Оценки"},
    {"resource": "students", "title": "Студенты"},
    {"resource": "teachers", "title": "Преподаватели"},
    {"resource": "finance",  "title": "Бухгалтерия"},
    {"resource": "users",    "title": "Пользователи"},
]


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    matched_role: str | None


class RBACService:
    def check(self, role: str, resource: str, action: str) -> PermissionResult:
        allowed_roles = ACL.get(resource, {}).get(action, set())
        if role in allowed_roles:
            return PermissionResult(True, role)
        return PermissionResult(False, None)

    def can_open_section(self, role: str, resource: str) -> bool:
        actions = ACL.get(resource, {})
        return any(role in allowed_roles for allowed_roles in actions.values())

    def allowed_menu(self, role: str) -> list[dict[str, str]]:
        return [item for item in MENU_SECTIONS if self.can_open_section(role, item["resource"])]

    def role_title(self, role: str) -> str:
        return ROLE_LABELS.get(role, role)

    def explain_permissions(self, role: str) -> dict[str, list[str]]:
        permissions: dict[str, list[str]] = {}
        for resource, actions in ACL.items():
            allowed = [action for action, roles in actions.items() if role in roles]
            if allowed:
                permissions[resource] = allowed
        return permissions

```

## services/utils.py
```python
from __future__ import annotations
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def grade_label(m: int) -> str:
    """Оценка по одному модулю: 25-34 Удовл., 35-44 Хорошо, 45-54 Отлично."""
    if m <= 0:
        return "—"
    if m <= 34:
        return "Удовл."
    if m <= 44:
        return "Хорошо"
    return "Отлично"

def format_name_initials(full_name: str) -> str:
    if not full_name: return "—"
    parts = full_name.split()
    if len(parts) >= 3:
        return f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
    elif len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."
    return full_name

ROLE_LABELS: dict[str, str] = {
    "student":       "Студент",
    "teacher":       "Преподаватель",
    "administrator": "Администратор",
    "accountant":    "Бухгалтер",
}

DAY_ORDER: dict[str, int] = {
    "Понедельник": 1,
    "Вторник":     2,
    "Среда":       3,
    "Четверг":     4,
    "Пятница":     5,
    "Суббота":     6,
}

```

## static/css/style.css
```css
:root {
    --bg-color: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.7);
    --accent-color: #38bdf8;
    --accent-hover: #0ea5e9;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --border-color: rgba(255, 255, 255, 0.1);
    --success-color: #10b981;
    --error-color: #ef4444;
    --warning-color: #f59e0b;
    --glass-blur: blur(12px);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-primary);
    line-height: 1.5;
    overflow-x: hidden;
    background-image: 
        radial-gradient(circle at 0% 0%, rgba(56, 189, 248, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 100% 100%, rgba(139, 92, 246, 0.15) 0%, transparent 50%);
    background-attachment: fixed;
}

/* Glassmorphism utility */
.glass {
    background: var(--card-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

/* Layout */
.app-container {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 280px;
    height: 100vh;
    position: fixed;
    padding: 2rem 1.5rem;
    display: flex;
    flex-direction: column;
    z-index: 100;
}

.main-content {
    flex: 1;
    margin-left: 280px;
    padding: 2rem;
}

/* Components */
.logo {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--accent-color);
    margin-bottom: 2.5rem;
    letter-spacing: -0.025em;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.nav-links {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.nav-item a {
    text-decoration: none;
    color: var(--text-secondary);
    padding: 0.75rem 1rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.2s ease;
    font-weight: 500;
}

.nav-item a:hover, .nav-item.active a {
    background: rgba(56, 189, 248, 0.1);
    color: var(--accent-color);
}

.nav-item.active a {
    box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.2);
}

.user-profile {
    margin-top: auto;
    padding: 1rem;
    border-top: 1px solid var(--border-color);
}

.user-name {
    display: block;
    font-weight: 600;
    font-size: 0.95rem;
}

.user-role {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.page-title {
    font-size: 1.875rem;
    font-weight: 700;
}

/* Cards */
.card {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* Table */
.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

th {
    text-align: left;
    padding: 1rem;
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.875rem;
    border-bottom: 1px solid var(--border-color);
}

td {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.95rem;
}

tr:hover td {
    background: rgba(255, 255, 255, 0.02);
}

/* Forms */
.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-secondary);
}

input, select, textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    outline: none;
    transition: border-color 0.2s;
}

input:focus {
    border-color: var(--accent-color);
}

.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.1s, opacity 0.2s;
}

.btn-primary {
    background: var(--accent-color);
    color: var(--bg-color);
}

.btn-primary:hover {
    background: var(--accent-hover);
}

.btn:active {
    transform: scale(0.98);
}

/* Login Page specifically */
.login-page {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.login-card {
    width: 100%;
    max-width: 400px;
    padding: 2.5rem;
}

.login-header {
    text-align: center;
    margin-bottom: 2rem;
}

.login-header h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.login-header p {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

/* Badge */
.badge {
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-success { background: rgba(16, 185, 129, 0.1); color: var(--success-color); }
.badge-error { background: rgba(239, 68, 68, 0.1); color: var(--error-color); }
.badge-warning { background: rgba(245, 158, 11, 0.1); color: var(--warning-color); }

/* Schedule specific */
.schedule-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
}

.day-card h3 {
    margin-bottom: 1rem;
    color: var(--accent-color);
    border-bottom: 2px solid rgba(56, 189, 248, 0.2);
    padding-bottom: 0.5rem;
}

.lesson-item {
    padding: 1rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.03);
    margin-bottom: 0.75rem;
    border-left: 4px solid var(--accent-color);
}

.lesson-time {
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.lesson-name {
    font-weight: 600;
    margin: 0.25rem 0;
}

.lesson-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
    display: flex;
    gap: 1rem;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.card, .main-content {
    animation: fadeIn 0.4s ease-out;
}

```

## templates/base.html
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Виртуальный Деканат{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar glass">
            <div class="logo">
                <i data-lucide="landmark" class="logo-icon"></i>
                <span>ДЕКАНАТ</span>
            </div>
            
            <nav class="nav-links">
                {% set menu = rbac.allowed_menu(current_user.role) %}
                <li class="nav-item {{ 'active' if request.endpoint == 'dashboard' }}">
                    <a href="{{ url_for('dashboard') }}">
                        <i data-lucide="layout-dashboard"></i>
                        Дашборд
                    </a>
                </li>
                {% for item in menu %}
                <li class="nav-item {{ 'active' if request.endpoint == item.resource }}">
                    <a href="{{ url_for(item.resource) }}">
                        {% if item.resource == 'schedule' %}
                            <i data-lucide="calendar"></i>
                        {% elif item.resource == 'grades' %}
                            <i data-lucide="bar-chart-3"></i>
                        {% elif item.resource == 'students' %}
                            <i data-lucide="graduation-cap"></i>
                        {% elif item.resource == 'teachers' %}
                            <i data-lucide="users"></i>
                        {% elif item.resource == 'finance' %}
                            <i data-lucide="wallet"></i>
                        {% elif item.resource == 'users' %}
                            <i data-lucide="settings"></i>
                        {% endif %}
                        {{ item.title }}
                    </a>
                </li>
                {% endfor %}
            </nav>
            
            <div class="user-profile">
                <div class="user-info">
                    <span class="user-name">{{ current_user.full_name }}</span>
                    <span class="user-role">{{ role_labels.get(current_user.role, current_user.role) }}</span>
                </div>
                <a href="{{ url_for('logout') }}" style="color: var(--error-color); text-decoration: none; font-size: 0.85rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i data-lucide="log-out" style="width: 14px; height: 14px;"></i>
                    Выйти
                </a>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, message in messages %}
                  <div class="card glass badge-{{ category }}" style="margin-bottom: 1rem; border: none;">{{ message }}</div>
                {% endfor %}
              {% endif %}
            {% endwith %}
            
            {% block content %}{% endblock %}
        </main>
    </div>
    <script>
        lucide.createIcons();
    </script>
</body>
</html>

```

## templates/dashboard.html
```html
{% extends "base.html" %}

{% block title %}Дашборд — Виртуальный Деканат{% endblock %}

{% block content %}
<div class="header">
    <h1 class="page-title">Добро пожаловать, {{ current_user.full_name }}!</h1>
</div>

<div class="grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
    <!-- Welcome Card -->
    <div class="card glass" style="grid-column: span 2;">
        <h2 style="margin-bottom: 1rem; color: var(--accent-color);">Сводная информация</h2>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Вы вошли как <strong>{{ role_labels.get(current_user.role) }}</strong>. Здесь вы можете быстро получить доступ к основным разделам системы.</p>
        
        {% if current_user.role == 'student' and student %}
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="lesson-item" style="border-left-color: var(--success-color);">
                <div class="user-role">Группа</div>
                <div class="lesson-name">{{ student.study_group }}</div>
            </div>
            <div class="lesson-item" style="border-left-color: var(--warning-color);">
                <div class="user-role">Зачётная книжка</div>
                <div class="lesson-name">{{ student.record_book }}</div>
            </div>
            <div class="lesson-item">
                <div class="user-role">Курс</div>
                <div class="lesson-name">{{ student.course }} курс</div>
            </div>
            <div class="lesson-item">
                <div class="user-role">Статус</div>
                <div class="lesson-name"><span class="badge badge-success">{{ student.status }}</span></div>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Quick Stats / Actions -->
    <div class="card glass">
        <h3 style="margin-bottom: 1.5rem;">Быстрые ссылки</h3>
        <div class="nav-links">
            <li class="nav-item">
                <a href="{{ url_for('schedule') }}" style="display: flex; align-items: center; gap: 0.5rem;">
                    <i data-lucide="calendar"></i> Посмотреть расписание
                </a>
            </li>
            {% if current_user.role == 'student' %}
            <li class="nav-item">
                <a href="{{ url_for('grades') }}" style="display: flex; align-items: center; gap: 0.5rem;">
                    <i data-lucide="bar-chart-3"></i> Мои оценки
                </a>
            </li>
            <li class="nav-item">
                <a href="{{ url_for('finance') }}" style="display: flex; align-items: center; gap: 0.5rem;">
                    <i data-lucide="wallet"></i> Финансы и оплата
                </a>
            </li>
            {% endif %}
            {% if current_user.role == 'administrator' %}
            <li class="nav-item">
                <a href="{{ url_for('users') }}" style="display: flex; align-items: center; gap: 0.5rem;">
                    <i data-lucide="settings"></i> Управление пользователями
                </a>
            </li>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

```

## templates/finance.html
```html
{% extends "base.html" %}
{% block title %}Бухгалтерия — Виртуальный Деканат{% endblock %}
{% block content %}
<div class="header">
    <h1 class="page-title">Финансовый учёт</h1>
    {% if current_user.role in ['administrator', 'accountant'] %}
    <button class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;" onclick="openModal()">
        <i data-lucide="plus" style="width: 18px; height: 18px;"></i> Создать операцию
    </button>
    {% endif %}
</div>

<div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
    <div class="card glass">
        <div style="color: var(--text-secondary); font-size: 0.9rem;">Общий баланс</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: var(--success-color); margin-top: 0.5rem;">
            {% set balance = 0 %}
            {% for f in finance_data %}{% set balance = balance + f.amount %}{% endfor %}
            {{ balance|round(2) }} ₽
        </div>
    </div>
</div>

<div class="card glass table-container">
    <table>
        <thead>
            <tr>
                <th>Дата</th>
                <th>Студент</th>
                <th>Тип</th>
                <th>Описание</th>
                <th>Сумма</th>
                <th>Статус</th>
                {% if current_user.role in ['administrator', 'accountant'] %}
                <th>Действие</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for f in finance_data %}
            <tr>
                <td>{{ f.date }}</td>
                <td>
                    {% if f.teacher_id %}
                        {{ teachers[f.teacher_id].full_name if f.teacher_id in teachers else 'Преподаватель' }} (П)
                    {% else %}
                        {{ students[f.student_id].full_name if f.student_id in students else 'Студент/Система' }}
                    {% endif %}
                </td>
                <td>
                    <span class="badge {{ 'badge-success' if f.op_type == 'Оплата' else 'badge-warning' }}">
                        {{ f.op_type }}
                    </span>
                </td>
                <td>{{ f.comment }}</td>
                <td style="font-weight: 600; color: {{ 'var(--success-color)' if f.amount > 0 else 'var(--error-color)' }}">
                    {{ f.amount }} ₽
                </td>
                <td><span class="badge badge-primary">{{ f.status }}</span></td>
                {% if current_user.role in ['administrator', 'accountant'] %}
                <td>
                    <form action="{{ url_for('delete_finance', op_id=f.id) }}" method="POST" style="display:inline;" onsubmit="return confirm('Удалить операцию?')">
                        <button type="submit" class="btn glass" style="padding: 0.3rem 0.6rem; color: var(--error-color);">
                            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                        </button>
                    </form>
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- Modal -->
<div id="financeModal" class="modal-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div class="card glass" style="width: 100%; max-width: 500px; padding: 2rem;">
        <h2 style="margin-bottom: 1.5rem; color: var(--accent-color);">Новая финансовая операция</h2>
        <form action="{{ url_for('add_finance') }}" method="POST">
            <div class="form-group">
                <label>Студент</label>
                <select name="student_id" required>
                    <option value="0">Система (Общее)</option>
                    {% for s in students.values() %}
                    <option value="{{ s.id }}">{{ s.full_name }} ({{ s.study_group }})</option>
                    {% endfor %}
                </select>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Тип операции</label>
                    <select name="type">
                        <option value="Оплата">Оплата</option>
                        <option value="Начисление">Начисление</option>
                        <option value="Штраф">Штраф</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Сумма (₽)</label>
                    <input type="number" step="0.01" name="amount" required placeholder="5000">
                </div>
            </div>
            
            <div class="form-group">
                <label>Описание</label>
                <input type="text" name="description" required placeholder="Оплата за семестр">
            </div>
            
            <div class="form-group">
                <label>Дата</label>
                <input type="date" name="date" value="2026-04-23">
            </div>
            
            <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem;">
                <button type="button" class="btn glass" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary">Создать</button>
            </div>
        </form>
    </div>
</div>

<script>
function openModal() {
    document.getElementById('financeModal').style.display = 'flex';
}
function closeModal() {
    document.getElementById('financeModal').style.display = 'none';
}
</script>
{% endblock %}

```

## templates/grades.html
```html
{% extends "base.html" %}

{% block title %}Оценки — Виртуальный Деканат{% endblock %}

{% block content %}
<div class="header">
    <h1 class="page-title">Журнал успеваемости</h1>
    {% if current_user.role in ['teacher', 'administrator'] %}
    <div style="display: flex; gap: 1rem; align-items: center;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 0.85rem; color: var(--text-secondary);">Группа:</span>
            <select class="glass" id="groupFilter" onchange="applyFilter()" style="padding: 0.4rem; width: auto;">
                <option value="Все">Все группы</option>
                {% for group in groups %}
                <option value="{{ group }}" {{ 'selected' if selected_group == group }}>{{ group }}</option>
                {% endfor %}
            </select>
        </div>
        <button class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;" onclick="openModal('add')">
            <i data-lucide="plus-circle" style="width: 18px; height: 18px;"></i> Выставить оценку
        </button>
    </div>
    {% endif %}
</div>

{% if current_user.role == 'student' %}
<div class="card glass" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem;">
    <div>
        <span style="color: var(--text-secondary);">Средний рейтинг:</span>
        {% set ns = namespace(total=0) %}
        {% set count = grades|length %}
        {% for g in grades %}
            {% set ns.total = ns.total + (g.m1 + g.m2) / 2.0 %}
        {% endfor %}
        <span style="font-size: 1.5rem; font-weight: 700; color: var(--success-color); margin-left: 0.5rem;">
            {{ (ns.total / count)|round(1) if count > 0 else '0.0' }}
        </span>
    </div>
    <select class="glass" id="semesterFilter" onchange="applyFilter()" style="width: auto; padding: 0.4rem 1rem;">
        {% for sem in all_semesters %}
        <option value="{{ sem }}" {{ 'selected' if selected_semester == sem }}>{{ sem }}</option>
        {% endfor %}
    </select>
</div>
{% endif %}

<div class="card glass table-container">
    <table>
        <thead>
            <tr>
                {% if current_user.role in ['teacher', 'administrator'] %}
                <th>Студент</th>
                {% endif %}
                <th>Дисциплина</th>
                <th>М1</th>
                <th>М2</th>
                <th>З (Зачет)</th>
                <th>Э (Экзамен)</th>
                <th>Коэфф.</th>
                <th>Итог</th>
                <th>Статус</th>
                {% if current_user.role in ['teacher', 'administrator'] %}
                <th>Действие</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for g in grades %}
            <tr>
                {% if current_user.role in ['teacher', 'administrator'] %}
                <td>{{ students[g.student_id].full_name }}</td>
                {% endif %}
                <td>{{ g.subject }}</td>
                <td>{{ g.m1 }}</td>
                <td>{{ g.m2 }}</td>
                <td><span class="{{ 'badge badge-success' if g.credit != '-' else '' }}">{{ g.credit }}</span></td>
                <td><span class="{{ 'badge badge-primary' if g.exam != '-' else '' }}">{{ g.exam }}</span></td>
                <td>{{ g.coefficient }}</td>
                <td>
                    <span style="font-weight: 700; color: var(--accent-color);">
                        {{ grade_label(((g.m1 + g.m2) / 2)|int) }}
                    </span>
                </td>
                <td><span class="badge badge-success">{{ g.status }}</span></td>
                {% if current_user.role in ['teacher', 'administrator'] %}
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn glass" style="padding: 0.3rem 0.6rem;" 
                                onclick='openModal("edit", {{ g|tojson }})'>
                            <i data-lucide="pencil" style="width: 14px; height: 14px;"></i>
                        </button>
                        <form action="{{ url_for('delete_grade', grade_id=g.id) }}" method="POST" style="display:inline;" onsubmit="return confirm('Удалить оценку?')">
                            <button type="submit" class="btn glass" style="padding: 0.3rem 0.6rem; color: var(--error-color);">
                                <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                            </button>
                        </form>
                    </div>
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- Modal -->
<div id="gradeModal" class="modal-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div class="card glass" style="width: 100%; max-width: 500px; padding: 2rem;">
        <h2 id="modalTitle" style="margin-bottom: 1.5rem; color: var(--accent-color);">Редактировать оценку</h2>
        <form id="gradeForm" action="{{ url_for('update_grade') }}" method="POST">
            <input type="hidden" name="grade_id" id="field_id">
            <input type="hidden" name="current_group" value="{{ selected_group if selected_group else '' }}">
            
            <div id="addFields" style="display: none;">
                <div class="form-group">
                    <label>Студент</label>
                    <select name="student_id" id="field_student_id">
                        {% for s in all_students %}
                        <option value="{{ s.id }}">{{ s.full_name }} ({{ s.study_group }})</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Дисциплина</label>
                    <select name="subject" id="field_subject">
                        {% for sub in teacher_subjects %}
                        <option value="{{ sub }}">{{ sub }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div id="studentInfo" style="margin-bottom: 1rem; font-weight: 600; color: var(--accent-color);"></div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Модуль 1</label>
                    <input type="number" name="m1" id="field_m1" min="0" max="54" value="0">
                </div>
                <div class="form-group">
                    <label>Модуль 2</label>
                    <input type="number" name="m2" id="field_m2" min="0" max="54" value="0">
                </div>
                <div class="form-group">
                    <label>Зачет (балл)</label>
                    <input type="text" name="credit" id="field_credit" value="-">
                </div>
                <div class="form-group">
                    <label>Экзамен (балл)</label>
                    <input type="text" name="exam" id="field_exam" value="-">
                </div>
                <div class="form-group">
                    <label>Коэффициент</label>
                    <input type="number" step="0.1" name="coefficient" id="field_coeff" value="1.0">
                </div>
            </div>
            
            <div class="form-group">
                <label>Статус</label>
                <select name="status" id="field_status">
                    <option value="Черновик">Черновик</option>
                    <option value="Подтверждена">Подтверждена</option>
                </select>
            </div>
            
            <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem;">
                <button type="button" class="btn glass" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
        </form>
    </div>
</div>

<script>
function applyFilter() {
    let url = new URL(window.location.href);
    
    const groupSelect = document.getElementById('groupFilter');
    if (groupSelect) {
        if (groupSelect.value !== 'Все') {
            url.searchParams.set('group', groupSelect.value);
        } else {
            url.searchParams.delete('group');
        }
    }
    
    const semSelect = document.getElementById('semesterFilter');
    if (semSelect) {
        url.searchParams.set('semester', semSelect.value);
    }
    
    window.location.href = url.toString();
}

function openModal(mode, gradeData = null) {
    const modal = document.getElementById('gradeModal');
    const title = document.getElementById('modalTitle');
    const addFields = document.getElementById('addFields');
    const studentInfo = document.getElementById('studentInfo');
    
    if (mode === 'edit' && gradeData) {
        title.innerText = "Редактировать оценку";
        addFields.style.display = 'none';
        studentInfo.style.display = 'block';
        studentInfo.innerText = gradeData.subject + " — " + (document.querySelector(`tr[onclick*="${gradeData.id}"] td:first-child`)?.innerText || "");
        
        document.getElementById('field_id').value = gradeData.id;
        document.getElementById('field_m1').value = gradeData.m1;
        document.getElementById('field_m2').value = gradeData.m2;
        document.getElementById('field_credit').value = gradeData.credit;
        document.getElementById('field_exam').value = gradeData.exam;
        document.getElementById('field_status').value = gradeData.status;
        document.getElementById('field_coeff').value = gradeData.coefficient || 1.0;
    } else {
        title.innerText = "Выставить новую оценку";
        addFields.style.display = 'block';
        studentInfo.style.display = 'none';
        
        document.getElementById('field_id').value = "";
        document.getElementById('field_m1').value = 0;
        document.getElementById('field_m2').value = 0;
        document.getElementById('field_credit').value = "-";
        document.getElementById('field_exam').value = "-";
        document.getElementById('field_coeff').value = 1.0;
        document.getElementById('field_status').value = "Черновик";
    }
    
    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('gradeModal').style.display = 'none';
}
</script>
{% endblock %}

```

## templates/login.html
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход — Виртуальный Деканат</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="login-page">
    <div class="login-card glass">
        <div class="login-header">
            <div style="margin-bottom: 1rem; color: var(--accent-color);">
                <i data-lucide="landmark" style="width: 48px; height: 48px;"></i>
            </div>
            <h1>Вход в систему</h1>
            <p>Добро пожаловать в Виртуальный Деканат</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="badge badge-error" style="display: block; margin-bottom: 1rem; text-align: center;">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        <form action="{{ url_for('login') }}" method="POST">
            <div class="form-group">
                <label for="login">Логин</label>
                <input type="text" id="login" name="login" required placeholder="admin_demo">
            </div>
            <div class="form-group">
                <label for="password">Пароль</label>
                <input type="password" id="password" name="password" required placeholder="••••••••">
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Войти</button>
        </form>
        
        <div style="margin-top: 2rem; font-size: 0.8rem; color: var(--text-secondary); text-align: center;">
            <p>Демо-данные:</p>
            <p>admin_demo / admin2026</p>
            <p>teacher_demo / teach2026</p>
            <p>student_demo / stud2026</p>
        </div>
    </div>
    <script>
        lucide.createIcons();
    </script>
</body>
</html>

```

## templates/schedule.html
```html
{% extends "base.html" %}

{% block title %}Расписание — Виртуальный Деканат{% endblock %}

{% block content %}
<div class="header">
    <h1 class="page-title">Расписание занятий</h1>
    <div style="display: flex; gap: 1rem; align-items: center;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 0.85rem; color: var(--text-secondary);">Группа:</span>
            <select class="glass" id="groupFilter" onchange="applyFilters()" style="padding: 0.4rem; width: auto;">
                <option value="Все">Все группы</option>
                {% for group in groups %}
                <option value="{{ group }}" {{ 'selected' if selected_group == group }}>{{ group }}</option>
                {% endfor %}
            </select>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 0.85rem; color: var(--text-secondary);">Преподаватель:</span>
            <select class="glass" id="teacherFilter" onchange="applyFilters()" style="padding: 0.4rem; width: auto;">
                <option value="Все">Все преподаватели</option>
                {% for teacher in teachers %}
                <option value="{{ teacher.id }}" {{ 'selected' if selected_teacher == teacher.id|string }}>{{ teacher.full_name }}</option>
                {% endfor %}
            </select>
        </div>
        {% if rbac.check(current_user.role, 'schedule', 'manage').allowed %}
        <button class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;" onclick="openModal('add')">
            <i data-lucide="plus" style="width: 18px; height: 18px;"></i> Добавить
        </button>
        {% endif %}
    </div>
</div>

<script>
function applyFilters() {
    const group = document.getElementById('groupFilter').value;
    const teacherId = document.getElementById('teacherFilter').value;
    let url = new URL(window.location.href);
    
    if (group !== 'Все') {
        url.searchParams.set('group', group);
    } else {
        url.searchParams.delete('group');
    }
    
    if (teacherId !== 'Все') {
        url.searchParams.set('teacher_id', teacherId);
    } else {
        url.searchParams.delete('teacher_id');
    }
    
    window.location.href = url.toString();
}
</script>

<div class="schedule-grid">
    {% for day in day_order %}
    <div class="schedule-day">
        <div class="day-header">{{ day }}</div>
        <div class="lesson-list">
            {% if schedule_data[day] %}
                {% for lesson in schedule_data[day] %}
                <div class="lesson-item card glass" style="position: relative;">
                    <div class="lesson-time">
                        <span class="pair-num">{{ lesson.pair }} пара</span>
                        <span class="time-range">{{ lesson.time }}</span>
                        {% if rbac.check(current_user.role, 'schedule', 'manage').allowed %}
                        <div style="position: absolute; top: 1rem; right: 1rem; display: flex; gap: 0.5rem;">
                            <button class="btn glass" style="padding: 0.2rem 0.4rem;" 
                                    onclick='openModal("edit", {{ lesson|tojson }})'>
                                <i data-lucide="pencil" style="width: 14px; height: 14px;"></i>
                            </button>
                            <form action="{{ url_for('delete_schedule', item_id=lesson.id) }}" method="POST" style="display:inline;" onsubmit="return confirm('Удалить занятие?')">
                                <button type="submit" class="btn glass" style="padding: 0.2rem 0.4rem; color: var(--error-color);">
                                    <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                                </button>
                            </form>
                        </div>
                        {% endif %}
                    </div>
                    <div class="lesson-name">{{ lesson.subject }}</div>
                    <div class="lesson-meta">
                        {% if selected_teacher and selected_teacher != 'Все' %}
                        <span style="color: var(--warning-color); font-weight: 600; display: flex; align-items: center; gap: 0.3rem;">
                            <i data-lucide="users" style="width: 14px; height: 14px;"></i> {{ lesson.study_group }}
                        </span>
                        {% else %}
                        <span style="display: flex; align-items: center; gap: 0.3rem;">
                            <i data-lucide="user" style="width: 14px; height: 14px;"></i> {{ format_name(lesson.teacher_name) }}
                        </span>
                        {% endif %}
                        <span style="display: flex; align-items: center; gap: 0.3rem;">
                            <i data-lucide="map-pin" style="width: 14px; height: 14px;"></i> {{ lesson.room }}
                        </span>
                        <span class="badge {{ 'badge-success' if lesson.format == 'Очная' else 'badge-warning' }}">{{ lesson.format }}</span>
                    </div>
                    <div class="lesson-type">{{ lesson.lesson_type }}</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-lessons">Нет занятий</div>
            {% endif %}
        </div>
    </div>
    {% endfor %}
</div>

<!-- Modal -->
<div id="scheduleModal" class="modal-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div class="card glass" style="width: 100%; max-width: 600px; padding: 2rem;">
        <h2 id="modalTitle" style="margin-bottom: 1.5rem; color: var(--accent-color);">Занятие</h2>
        <form id="scheduleForm" action="{{ url_for('add_schedule') }}" method="POST">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>День недели</label>
                    <select name="day" id="f_day">
                        {% for d in day_order %}
                        <option value="{{ d }}">{{ d }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Пара (1-8)</label>
                    <input type="number" name="pair" id="f_pair" min="1" max="8" required>
                </div>
                <div class="form-group">
                    <label>Время (чч:мм - чч:мм)</label>
                    <input type="text" name="time" id="f_time" required placeholder="09:00 - 10:30">
                </div>
                <div class="form-group">
                    <label>Группа</label>
                    <input type="text" name="study_group" id="f_group" required>
                </div>
            </div>

            <div class="form-group">
                <label>Предмет</label>
                <input type="text" name="subject" id="f_subject" required>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Преподаватель</label>
                    <select name="teacher_id" id="f_teacher">
                        {% for t in teachers %}
                        <option value="{{ t.id }}">{{ t.full_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Аудитория</label>
                    <input type="text" name="room" id="f_room">
                </div>
                <div class="form-group">
                    <label>Тип</label>
                    <select name="lesson_type" id="f_type">
                        <option value="Лекция">Лекция</option>
                        <option value="Практика">Практика</option>
                        <option value="Лаб. работа">Лаб. работа</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Формат</label>
                    <select name="format" id="f_format">
                        <option value="Очная">Очная</option>
                        <option value="Дистанционная">Дистанционная</option>
                    </select>
                </div>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem;">
                <button type="button" class="btn glass" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary" id="submitBtn">Сохранить</button>
            </div>
        </form>
    </div>
</div>

<script>
function openModal(mode, data = null) {
    const modal = document.getElementById('scheduleModal');
    const form = document.getElementById('scheduleForm');
    const title = document.getElementById('modalTitle');
    const btn = document.getElementById('submitBtn');
    
    if (mode === 'edit' && data) {
        title.innerText = "Редактировать занятие";
        btn.innerText = "Сохранить";
        form.action = "/schedule/edit/" + data.id;
        
        document.getElementById('f_day').value = data.day;
        document.getElementById('f_pair').value = data.pair;
        document.getElementById('f_time').value = data.time;
        document.getElementById('f_group').value = data.study_group;
        document.getElementById('f_subject').value = data.subject;
        document.getElementById('f_teacher').value = data.teacher_id;
        document.getElementById('f_room').value = data.room;
        document.getElementById('f_type').value = data.lesson_type;
        document.getElementById('f_format').value = data.format;
    } else {
        title.innerText = "Добавить занятие";
        btn.innerText = "Добавить";
        form.action = "{{ url_for('add_schedule') }}";
        form.reset();
    }
    modal.style.display = 'flex';
}
function closeModal() {
    document.getElementById('scheduleModal').style.display = 'none';
}
</script>
{% endblock %}

```

## templates/students.html
```html
{% extends "base.html" %}
{% block title %}Студенты — Виртуальный Деканат{% endblock %}
{% block content %}
<div class="header">
    <h1 class="page-title">Управление студентами</h1>
    {% if rbac.check(current_user.role, 'students', 'manage').allowed %}
    <button class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;" onclick="openModal('add')">
        <i data-lucide="user-plus" style="width: 18px; height: 18px;"></i> Добавить студента
    </button>
    {% endif %}
</div>

<div class="card glass table-container">
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>ФИО</th>
                <th>Группа</th>
                <th>Зачётная книжка</th>
                <th>Курс</th>
                <th>Статус</th>
                {% if rbac.check(current_user.role, 'students', 'manage').allowed %}
                <th>Действия</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for s in students %}
            <tr>
                <td>{{ s.id }}</td>
                <td>{{ s.full_name }}</td>
                <td>{{ s.study_group }}</td>
                <td>{{ s.record_book }}</td>
                <td>{{ s.course }}</td>
                <td><span class="badge badge-success">{{ s.status }}</span></td>
                {% if rbac.check(current_user.role, 'students', 'manage').allowed %}
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn glass" style="padding: 0.3rem 0.6rem;" 
                                onclick='openModal("edit", {{ s|tojson }})'>
                            <i data-lucide="pencil" style="width: 14px; height: 14px;"></i>
                        </button>
                        <form action="{{ url_for('delete_student', student_id=s.id) }}" method="POST" style="display:inline;" onsubmit="return confirm('Удалить студента?')">
                            <button type="submit" class="btn glass" style="padding: 0.3rem 0.6rem; color: var(--error-color);">
                                <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                            </button>
                        </form>
                    </div>
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- Modal -->
<div id="studentModal" class="modal-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div class="card glass" style="width: 100%; max-width: 500px; padding: 2rem;">
        <h2 id="modalTitle" style="margin-bottom: 1.5rem; color: var(--accent-color);">Добавить студента</h2>
        <form id="studentForm" action="{{ url_for('add_student') }}" method="POST">
            <div class="form-group">
                <label>ФИО студента</label>
                <input type="text" name="full_name" id="f_name" required>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Группа</label>
                    <input type="text" name="study_group" id="f_group" required>
                </div>
                <div class="form-group">
                    <label>Зачётная книжка</label>
                    <input type="text" name="record_book" id="f_record" required>
                </div>
                <div class="form-group">
                    <label>Курс</label>
                    <input type="number" name="course" id="f_course" min="1" max="6" value="1">
                </div>
                <div class="form-group">
                    <label>Статус</label>
                    <select name="status" id="f_status">
                        <option value="Активен">Активен</option>
                        <option value="Академ">Академ</option>
                        <option value="Отчислен">Отчислен</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>Направление</label>
                <input type="text" name="program" id="f_program">
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Форма</label>
                    <select name="study_form" id="f_form">
                        <option value="Очная">Очная</option>
                        <option value="Заочная">Заочная</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Основание</label>
                    <select name="funding" id="f_funding">
                        <option value="Бюджет">Бюджет</option>
                        <option value="Договор">Договор</option>
                    </select>
                </div>
            </div>
            
            <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem;">
                <button type="button" class="btn glass" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary" id="submitBtn">Добавить</button>
            </div>
        </form>
    </div>
</div>

<script>
function openModal(mode, data = null) {
    const modal = document.getElementById('studentModal');
    const form = document.getElementById('studentForm');
    const title = document.getElementById('modalTitle');
    const btn = document.getElementById('submitBtn');
    
    if (mode === 'edit' && data) {
        title.innerText = "Редактировать данные";
        btn.innerText = "Сохранить";
        form.action = "/students/edit/" + data.id;
        
        document.getElementById('f_name').value = data.full_name;
        document.getElementById('f_group').value = data.study_group;
        document.getElementById('f_record').value = data.record_book;
        document.getElementById('f_course').value = data.course;
        document.getElementById('f_program').value = data.program;
        document.getElementById('f_status').value = data.status;
        document.getElementById('f_form').value = data.study_form;
        document.getElementById('f_funding').value = data.funding;
    } else {
        title.innerText = "Добавить нового студента";
        btn.innerText = "Добавить";
        form.action = "{{ url_for('add_student') }}";
        form.reset();
    }
    modal.style.display = 'flex';
}
function closeModal() {
    document.getElementById('studentModal').style.display = 'none';
}
</script>
{% endblock %}

```

## templates/teachers.html
```html
{% extends "base.html" %}
{% block title %}Преподаватели — Виртуальный Деканат{% endblock %}
{% block content %}
<div class="header">
    <h1 class="page-title">Преподавательский состав</h1>
    {% if rbac.check(current_user.role, 'teachers', 'manage').allowed %}
    <button class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;" onclick="openModal('add')">
        <i data-lucide="user-plus" style="width: 18px; height: 18px;"></i> Добавить преподавателя
    </button>
    {% endif %}
</div>

<div class="card glass table-container">
    <table>
        <thead>
            <tr>
                <th>ФИО</th>
                <th>Кафедра</th>
                <th>Должность</th>
                <th>Дисциплины</th>
                <th>Контакты</th>
                {% if rbac.check(current_user.role, 'teachers', 'manage').allowed %}
                <th>Действия</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for t in teachers %}
            <tr>
                <td><strong>{{ t.full_name }}</strong></td>
                <td>{{ t.department }}</td>
                <td>{{ t.position }} ({{ t.degree }})</td>
                <td>
                    {% for sub in t.subjects %}
                    <span class="badge badge-primary" style="margin-right: 0.2rem; margin-bottom: 0.2rem; display: inline-block;">{{ sub }}</span>
                    {% endfor %}
                </td>
                <td>{{ t.contacts }}</td>
                {% if rbac.check(current_user.role, 'teachers', 'manage').allowed %}
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn glass" style="padding: 0.3rem 0.6rem;" 
                                onclick='openModal("edit", {{ t|tojson }})'>
                            <i data-lucide="pencil" style="width: 14px; height: 14px;"></i>
                        </button>
                        <form action="{{ url_for('delete_teacher', teacher_id=t.id) }}" method="POST" style="display:inline;" onsubmit="return confirm('Удалить преподавателя?')">
                            <button type="submit" class="btn glass" style="padding: 0.3rem 0.6rem; color: var(--error-color);">
                                <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                            </button>
                        </form>
                    </div>
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- Modal -->
<div id="teacherModal" class="modal-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div class="card glass" style="width: 100%; max-width: 600px; padding: 2rem;">
        <h2 id="modalTitle" style="margin-bottom: 1.5rem; color: var(--accent-color);">Преподаватель</h2>
        <form id="teacherForm" action="{{ url_for('add_teacher') }}" method="POST">
            <div class="form-group">
                <label>ФИО</label>
                <input type="text" name="full_name" id="f_name" required placeholder="Петров Петр Петрович">
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Кафедра</label>
                    <input type="text" name="department" id="f_dept" required placeholder="ИУ5">
                </div>
                <div class="form-group">
                    <label>Должность</label>
                    <input type="text" name="position" id="f_pos" placeholder="Доцент">
                </div>
                <div class="form-group">
                    <label>Степень</label>
                    <input type="text" name="degree" id="f_deg" placeholder="к.т.н.">
                </div>
                <div class="form-group">
                    <label>Контакты</label>
                    <input type="text" name="contacts" id="f_contact" placeholder="petrov@mstu.ru">
                </div>
            </div>
            
            <div class="form-group">
                <label>Дисциплины (через запятую)</label>
                <textarea name="subjects" id="f_subs" rows="3" placeholder="Программирование, Базы данных"></textarea>
            </div>
            
            <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem;">
                <button type="button" class="btn glass" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary" id="submitBtn">Сохранить</button>
            </div>
        </form>
    </div>
</div>

<script>
function openModal(mode, data = null) {
    const modal = document.getElementById('teacherModal');
    const form = document.getElementById('teacherForm');
    const title = document.getElementById('modalTitle');
    const btn = document.getElementById('submitBtn');
    
    if (mode === 'edit' && data) {
        title.innerText = "Редактировать данные";
        btn.innerText = "Сохранить";
        form.action = "/teachers/edit/" + data.id;
        
        document.getElementById('f_name').value = data.full_name;
        document.getElementById('f_dept').value = data.department;
        document.getElementById('f_pos').value = data.position;
        document.getElementById('f_deg').value = data.degree;
        document.getElementById('f_contact').value = data.contacts;
        document.getElementById('f_subs').value = data.subjects ? data.subjects.join(', ') : "";
    } else {
        title.innerText = "Добавить преподавателя";
        btn.innerText = "Добавить";
        form.action = "{{ url_for('add_teacher') }}";
        form.reset();
    }
    modal.style.display = 'flex';
}
function closeModal() {
    document.getElementById('teacherModal').style.display = 'none';
}
</script>
{% endblock %}

```

## templates/users.html
```html
{% extends "base.html" %}
{% block title %}Пользователи — Виртуальный Деканат{% endblock %}
{% block content %}
<div class="header">
    <h1 class="page-title">Управление доступом</h1>
    {% if rbac.check(current_user.role, 'users', 'manage').allowed %}
    <button class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;" onclick="openModal('add')">
        <i data-lucide="user-plus" style="width: 18px; height: 18px;"></i> Новый пользователь
    </button>
    {% endif %}
</div>

<div class="card glass table-container">
    <table>
        <thead>
            <tr>
                <th>Логин</th>
                <th>Роль</th>
                <th>ФИО</th>
                <th>Студент ID</th>
                <th>Препод ID</th>
                {% if rbac.check(current_user.role, 'users', 'manage').allowed %}
                <th>Действия</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for u in users %}
            <tr>
                <td><strong>{{ u.login }}</strong></td>
                <td><span class="badge badge-primary">{{ role_labels.get(u.role, u.role) }}</span></td>
                <td>{{ u.full_name }}</td>
                <td>{{ u.student_id or '—' }}</td>
                <td>{{ u.teacher_id or '—' }}</td>
                {% if rbac.check(current_user.role, 'users', 'manage').allowed %}
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn glass" style="padding: 0.3rem 0.6rem;" 
                                onclick='openModal("edit", {{ u|tojson }})'>
                            <i data-lucide="pencil" style="width: 14px; height: 14px;"></i>
                        </button>
                        <form action="{{ url_for('delete_user', login=u.login) }}" method="POST" style="display:inline;" onsubmit="return confirm('Удалить пользователя?')">
                            <button type="submit" class="btn glass" style="padding: 0.3rem 0.6rem; color: var(--error-color);">
                                <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                            </button>
                        </form>
                    </div>
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- Modal -->
<div id="userModal" class="modal-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div class="card glass" style="width: 100%; max-width: 500px; padding: 2rem;">
        <h2 id="modalTitle" style="margin-bottom: 1.5rem; color: var(--accent-color);">Пользователь</h2>
        <form id="userForm" action="{{ url_for('add_user') }}" method="POST">
            <div class="form-group">
                <label>Логин</label>
                <input type="text" name="login" id="f_login" required>
            </div>
            <div class="form-group" id="passGroup">
                <label>Пароль</label>
                <input type="password" name="password" id="f_pass">
            </div>
            <div class="form-group">
                <label>Полное имя</label>
                <input type="text" name="full_name" id="f_name" required>
            </div>
            <div class="form-group">
                <label>Роль</label>
                <select name="role" id="f_role">
                    {% for r, label in role_labels.items() %}
                    <option value="{{ r }}">{{ label }}</option>
                    {% endfor %}
                </select>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Студент ID (опц.)</label>
                    <input type="number" name="student_id" id="f_sid">
                </div>
                <div class="form-group">
                    <label>Преподаватель ID (опц.)</label>
                    <input type="number" name="teacher_id" id="f_tid">
                </div>
            </div>
            
            <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem;">
                <button type="button" class="btn glass" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary" id="submitBtn">Сохранить</button>
            </div>
        </form>
    </div>
</div>

<script>
function openModal(mode, data = null) {
    const modal = document.getElementById('userModal');
    const form = document.getElementById('userForm');
    const title = document.getElementById('modalTitle');
    const passGroup = document.getElementById('passGroup');
    const btn = document.getElementById('submitBtn');
    
    if (mode === 'edit' && data) {
        title.innerText = "Редактировать пользователя";
        btn.innerText = "Сохранить";
        form.action = "/users/edit/" + data.login;
        passGroup.style.display = 'none';
        
        document.getElementById('f_login').value = data.login;
        document.getElementById('f_login').readOnly = true;
        document.getElementById('f_name').value = data.full_name;
        document.getElementById('f_role').value = data.role;
        document.getElementById('f_sid').value = data.student_id || "";
        document.getElementById('f_tid').value = data.teacher_id || "";
    } else {
        title.innerText = "Создать нового пользователя";
        btn.innerText = "Создать";
        form.action = "{{ url_for('add_user') }}";
        form.reset();
        passGroup.style.display = 'block';
        document.getElementById('f_login').readOnly = false;
    }
    modal.style.display = 'flex';
}
function closeModal() {
    document.getElementById('userModal').style.display = 'none';
}
</script>
{% endblock %}

```


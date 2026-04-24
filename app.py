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

# =====================================================
# ВИРТУАЛЬНЫЙ ДЕКАНАТ - ПОЛНАЯ ВЕРСИЯ
# Студент: Слисаренко Дарья
# Вариант: RBAC + ACL (комбинированный подход)
# =====================================================

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime
from abc import ABC, abstractmethod

# =====================================================
# ЧАСТЬ 1: АУТЕНТИФИКАЦИЯ (2 варианта)
# =====================================================

class Authenticator(ABC):
    """Абстрактный класс для аутентификации"""
    @abstractmethod
    def authenticate(self, login, password):
        pass

class PasswordAuthenticator(Authenticator):
    """Вариант 1: Аутентификация по паролю"""
    def authenticate(self, login, password):
        users = self._load_users()
        if login in users and users[login]["password"] == password:
            return users[login]
        return None
    
    def _load_users(self):
        return {
            "dispetcher": {"password": "123", "role": "Диспетчерская служба", "full_name": "Петрова А.С.", "department": "Учебный отдел"},
            "zav_kaf": {"password": "456", "role": "Заведующий кафедрой", "full_name": "Сидоров И.И.", "department": "Кафедра ИТ"},
            "teacher": {"password": "789", "role": "Преподаватель", "full_name": "Иванов В.В.", "department": "Кафедра ИТ"},
            "student": {"password": "000", "role": "Студент", "full_name": "Смирнова Е.А.", "group": "ИВТ-41"},
            "methodist": {"password": "111", "role": "Методист", "full_name": "Козлова М.И.", "department": "Учебный отдел"},
            "accountant": {"password": "222", "role": "Бухгалтерия", "full_name": "Соколова Т.П.", "department": "Бухгалтерия"},
        }

class TokenAuthenticator(Authenticator):
    """Вариант 2: Аутентификация по токену (демо-версия)"""
    def authenticate(self, token, password=None):
        # В реальной системе здесь была бы проверка JWT токена
        tokens = {
            "TOKEN_123": "dispetcher",
            "TOKEN_456": "teacher",
            "TOKEN_789": "student"
        }
        if token in tokens:
            login = tokens[token]
            users = PasswordAuthenticator()._load_users()
            return users.get(login)
        return None

# =====================================================
# ЧАСТЬ 2: ACL (Access Control List) для объектов
# =====================================================

class ACLManager:
    """
    ACL - список прав доступа к объектам
    Формат: {объект: {роль: [действия]}}
    """
    def __init__(self):
        self.acl = self._init_acl()
    
    def _init_acl(self):
        return {
            # Объект "Расписание"
            "Schedule": {
                "Диспетчерская служба": ["read", "create", "update", "delete", "publish"],
                "Заведующий кафедрой": ["read", "approve", "comment"],
                "Преподаватель": ["read", "request_change"],
                "Студент": ["read"],
                "Методист": ["read", "edit"],
                "Бухгалтерия": ["read"]
            },
            # Объект "Успеваемость"
            "Grades": {
                "Диспетчерская служба": ["read"],
                "Заведующий кафедрой": ["read", "review"],
                "Преподаватель": ["read", "create", "update"],
                "Студент": ["read"],
                "Методист": ["read", "edit"],
                "Бухгалтерия": ["read"]
            },
            # Объект "Пользователи"
            "Users": {
                "Диспетчерская служба": ["read", "create", "update", "delete"],
                "Заведующий кафедрой": ["read"],
                "Преподаватель": [],
                "Студент": [],
                "Методист": ["read"],
                "Бухгалтерия": []
            },
            # Объект "Финансы"
            "Finance": {
                "Диспетчерская служба": [],
                "Заведующий кафедрой": ["read_staff_salary"],
                "Преподаватель": ["read_own_salary"],
                "Студент": [],
                "Методист": [],
                "Бухгалтерия": ["read", "create", "update", "delete"]
            }
        }
    
    def check_permission(self, role, obj, action):
        """Проверка, имеет ли роль доступ к объекту с указанным действием"""
        if obj in self.acl and role in self.acl[obj]:
            return action in self.acl[obj][role]
        return False
    
    def get_permissions(self, role, obj):
        """Получить все разрешения роли для объекта"""
        if obj in self.acl and role in self.acl[obj]:
            return self.acl[obj][role]
        return []

# =====================================================
# ЧАСТЬ 3: RBAC (Role-Based Access Control)
# =====================================================

class RoleHierarchy:
    """
    Иерархия ролей с наследованием прав
    Более высокий уровень включает права нижних
    """
    def __init__(self):
        self.hierarchy = {
            "Администратор": ["Методист", "Диспетчерская служба", "Заведующий кафедрой", "Преподаватель", "Студент", "Бухгалтерия"],
            "Заведующий кафедрой": ["Преподаватель"],
            "Методист": ["Диспетчерская служба"],
            "Диспетчерская служба": [],
            "Преподаватель": [],
            "Студент": [],
            "Бухгалтерия": []
        }
    
    def get_inherited_roles(self, role):
        """Получить все роли, права которых наследует данная роль"""
        inherited = []
        if role in self.hierarchy:
            inherited.extend(self.hierarchy[role])
            for subrole in self.hierarchy[role]:
                inherited.extend(self.get_inherited_roles(subrole))
        return list(set(inherited))

class SeparationOfDuties:
    """
    Статическое и динамическое разделение обязанностей
    """
    def __init__(self):
        # Статическое разделение (нельзя иметь две конфликтующие роли одновременно)
        self.static_separation = [
            {"role1": "Бухгалтерия", "role2": "Диспетчерская служба"},  # Нельзя быть и бухгалтером, и диспетчером
            {"role1": "Заведующий кафедрой", "role2": "Студент"}  # Нельзя быть завкафедрой и студентом
        ]
        
        # Динамическое разделение (нельзя выполнить два конфликтующих действия в одной сессии)
        self.dynamic_separation = [
            {"action1": "create_user", "action2": "delete_user"},  # Нельзя создать и удалить пользователя в одной сессии
            {"action1": "update_grades", "action2": "approve_grades"}  # Нельзя обновить и утвердить оценки
        ]
    
    def check_static_separation(self, roles):
        """Проверка статического разделения обязанностей"""
        for rule in self.static_separation:
            if rule["role1"] in roles and rule["role2"] in roles:
                return False, f"Конфликт ролей: {rule['role1']} и {rule['role2']}"
        return True, "OK"
    
    def check_dynamic_separation(self, actions_taken, new_action):
        """Проверка динамического разделения обязанностей"""
        for rule in self.dynamic_separation:
            if new_action in [rule["action1"], rule["action2"]]:
                conflict_action = rule["action2"] if new_action == rule["action1"] else rule["action1"]
                if conflict_action in actions_taken:
                    return False, f"Конфликт действий: {new_action} и {conflict_action} в одной сессии"
        return True, "OK"

# =====================================================
# МОДЕЛИ ДАННЫХ (предметная область)
# =====================================================

class Department:
    """Кафедра"""
    def __init__(self, id, name, institute):
        self.id = id
        self.name = name
        self.institute = institute
        self.teachers = []
        self.disciplines = []

class Institute:
    """Институт"""
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.departments = []

class Teacher:
    """Преподаватель"""
    def __init__(self, id, full_name, position, department, academic_degree):
        self.id = id
        self.full_name = full_name
        self.position = position  # должность
        self.department = department
        self.academic_degree = academic_degree  # ученая степень
        self.disciplines = []

class Discipline:
    """Дисциплина"""
    def __init__(self, id, name, department, hours, control_type):
        self.id = id
        self.name = name
        self.department = department
        self.hours = hours
        self.control_type = control_type  # "Экзамен" или "Зачёт"
        self.teacher = None

class Student:
    """Студент"""
    def __init__(self, id, full_name, group, year):
        self.id = id
        self.full_name = full_name
        self.group = group
        self.year = year
        self.grades = []

# =====================================================
# ЗАГРУЗКА ДАННЫХ ИЗ ФАЙЛОВ (для демонстрации архитектуры)
# =====================================================

class DataManager:
    """Управление данными с возможностью сохранения/загрузки"""
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из JSON файлов"""
        # Расписание
        self.schedule = self._load_json("schedule.json", self._default_schedule())
        # Успеваемость
        self.grades = self._load_json("grades.json", self._default_grades())
        # Пользователи
        self.users = self._load_json("users.json", self._default_users())
        # Преподаватели
        self.teachers = self._load_json("teachers.json", self._default_teachers())
        # Дисциплины
        self.disciplines = self._load_json("disciplines.json", self._default_disciplines())
    
    def _load_json(self, filename, default):
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filename, data):
        path = os.path.join(self.data_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_all(self):
        """Сохранить все данные"""
        self._save_json("schedule.json", self.schedule)
        self._save_json("grades.json", self.grades)
        self._save_json("users.json", self.users)
    
    def _default_schedule(self):
        return {
            "Понедельник": [
                {"pair": 1, "time": "8:30-10:10", "subject": "Математика", "room": "0211", 
                 "teacher": "Проф. Иванов", "type": "Лекция", "format": "Очно", "period": "10.02-14.04"},
                {"pair": 2, "time": "10:20-12:00", "subject": "Физика", "room": "0304", 
                 "teacher": "Доц. Петров", "type": "Лабораторная", "format": "Очно", "period": "19.02-12.03"},
                {"pair": 3, "time": "12:20-14:00", "subject": "Английский язык", "room": "401", 
                 "teacher": "Ст. Денисова", "type": "Семинар", "format": "Очно", "period": "27.02-10.04"},
            ],
            "Вторник": [
                {"pair": 1, "time": "8:30-10:10", "subject": "Программирование", "room": "0211", 
                 "teacher": "Проф. Сидоров", "type": "Лекция", "format": "Дистант", "period": "10.02-14.04"},
                {"pair": 3, "time": "12:20-14:00", "subject": "Базы данных", "room": "401", 
                 "teacher": "Доц. Смирнова", "type": "Лабораторная", "format": "Очно", "period": "19.02-12.03"},
                {"pair": 4, "time": "14:10-15:50", "subject": "Web-технологии", "room": "0304", 
                 "teacher": "Проф. Козлов", "type": "Семинар", "format": "Очно", "period": "27.02-10.04"},
            ],
            "Среда": [
                {"pair": 1, "time": "8:30-10:10", "subject": "Компьютерные сети", "room": "0211", 
                 "teacher": "Доц. Воробьёва", "type": "Лекция", "format": "Очно", "period": "10.02-14.04"},
                {"pair": 3, "time": "12:20-14:00", "subject": "Информационная безопасность", "room": "401", 
                 "teacher": "Проф. Соколов", "type": "Лабораторная", "format": "Очно", "period": "19.02-12.03"},
                {"pair": 5, "time": "16:00-17:40", "subject": "Операционные системы", "room": "0304", 
                 "teacher": "Проф. Новиков", "type": "Семинар", "format": "Дистант", "period": "27.02-10.04"},
            ],
            "Четверг": [
                {"pair": 2, "time": "10:20-12:00", "subject": "Дискретная математика", "room": "0211", 
                 "teacher": "Доц. Морозова", "type": "Лекция", "format": "Очно", "period": "10.02-14.04"},
                {"pair": 4, "time": "14:10-15:50", "subject": "Экономика", "room": "401", 
                 "teacher": "Доц. Лебедева", "type": "Семинар", "format": "Очно", "period": "19.02-12.03"},
                {"pair": 5, "time": "16:00-17:40", "subject": "Методология науки", "room": "0211", 
                 "teacher": "Проф. Андреев", "type": "Лекция", "format": "Очно", "period": "10.02-14.04"},
            ],
            "Пятница": [
                {"pair": 1, "time": "8:30-10:10", "subject": "Машинное обучение", "room": "0211", 
                 "teacher": "Проф. Орлов", "type": "Лекция", "format": "Дистант", "period": "10.02-14.04"},
                {"pair": 4, "time": "14:10-15:50", "subject": "Анализ данных", "room": "0304", 
                 "teacher": "Доц. Крылова", "type": "Лабораторная", "format": "Очно", "period": "27.02-10.04"},
            ],
            "Суббота": [
                {"pair": 1, "time": "8:30-10:10", "subject": "Физическая культура", "room": "Спортзал", 
                 "teacher": "Ст. Орлов", "type": "Семинар", "format": "Очно", "period": "10.02-31.05"},
                {"pair": 2, "time": "10:20-12:00", "subject": "Управление проектами", "room": "401", 
                 "teacher": "Доц. Белова", "type": "Семинар", "format": "Очно", "period": "19.02-12.03"},
                {"pair": 3, "time": "12:20-14:00", "subject": "Психология", "room": "0211", 
                 "teacher": "Доц. Михайлова", "type": "Лекция", "format": "Очно", "period": "10.02-31.05"},
                {"pair": 4, "time": "14:10-15:50", "subject": "Риторика", "room": "401", 
                 "teacher": "Ст. Павлова", "type": "Семинар", "format": "Очно", "period": "19.02-12.03"},
                {"pair": 5, "time": "16:00-17:40", "subject": "Правоведение", "room": "0304", 
                 "teacher": "Проф. Степанов", "type": "Лекция", "format": "Дистант", "period": "27.02-10.04"},
            ],
        }
    
    def _default_grades(self):
        return {
            "Смирнова Е.А.": {
                "2025 - осень": [
                    {"subject": "Математика", "m1": 38, "m2": 42, "exam": 40, "credit": None, "coefficient": 2.5},
                    {"subject": "Физика", "m1": 35, "m2": 36, "exam": 34, "credit": None, "coefficient": 2.0},
                    {"subject": "Программирование", "m1": 45, "m2": 48, "exam": 50, "credit": None, "coefficient": 3.0},
                ],
                "2026 - весна": [
                    {"subject": "Информационные системы", "m1": 42, "m2": 48, "exam": 50, "credit": None, "coefficient": 2.8},
                    {"subject": "Базы данных", "m1": 38, "m2": 40, "exam": 45, "credit": None, "coefficient": 2.5},
                    {"subject": "Web-технологии", "m1": 35, "m2": 38, "exam": 42, "credit": None, "coefficient": 2.2},
                    {"subject": "Машинное обучение", "m1": 40, "m2": 42, "exam": 48, "credit": None, "coefficient": 3.0},
                    {"subject": "Анализ данных", "m1": 36, "m2": 39, "exam": 44, "credit": None, "coefficient": 2.6},
                    {"subject": "Управление проектами", "m1": 32, "m2": 35, "exam": None, "credit": 78, "coefficient": 1.5},
                    {"subject": "Физическая культура", "m1": None, "m2": None, "exam": None, "credit": 85, "coefficient": 1.0},
                    {"subject": "Психология", "m1": 40, "m2": 42, "exam": None, "credit": 82, "coefficient": 1.8},
                    {"subject": "Риторика", "m1": 38, "m2": 40, "exam": None, "credit": 75, "coefficient": 1.2},
                    {"subject": "Правоведение", "m1": 35, "m2": 37, "exam": None, "credit": 70, "coefficient": 1.0},
                ],
                "2026 - осень": [
                    {"subject": "Компьютерные сети", "m1": 30, "m2": 35, "exam": 40, "credit": None, "coefficient": 2.4},
                    {"subject": "Информационная безопасность", "m1": 32, "m2": 36, "exam": 42, "credit": None, "coefficient": 2.7},
                    {"subject": "Операционные системы", "m1": 28, "m2": 34, "exam": 38, "credit": None, "coefficient": 2.3},
                    {"subject": "Дипломное проектирование", "m1": None, "m2": None, "exam": None, "credit": 90, "coefficient": 0.8},
                ],
            }
        }
    
    def _default_users(self):
        return {
            "dispetcher": {"password": "123", "role": "Диспетчерская служба", "full_name": "Петрова А.С.", "department": "Учебный отдел"},
            "zav_kaf": {"password": "456", "role": "Заведующий кафедрой", "full_name": "Сидоров И.И.", "department": "Кафедра ИТ"},
            "teacher": {"password": "789", "role": "Преподаватель", "full_name": "Иванов В.В.", "department": "Кафедра ИТ"},
            "student": {"password": "000", "role": "Студент", "full_name": "Смирнова Е.А.", "group": "ИВТ-41"},
            "methodist": {"password": "111", "role": "Методист", "full_name": "Козлова М.И.", "department": "Учебный отдел"},
            "accountant": {"password": "222", "role": "Бухгалтерия", "full_name": "Соколова Т.П.", "department": "Бухгалтерия"},
        }
    
    def _default_teachers(self):
        return [
            {"id": 1, "full_name": "Иванов В.В.", "position": "Профессор", "department": "Кафедра ИТ", "degree": "д.т.н."},
            {"id": 2, "full_name": "Петров А.С.", "position": "Доцент", "department": "Кафедра ИТ", "degree": "к.ф.-м.н."},
            {"id": 3, "full_name": "Сидоров И.И.", "position": "Профессор", "department": "Кафедра ИТ", "degree": "д.ф.-м.н."},
            {"id": 4, "full_name": "Смирнова Е.А.", "position": "Доцент", "department": "Кафедра ИТ", "degree": "к.т.н."},
        ]
    
    def _default_disciplines(self):
        return [
            {"id": 1, "name": "Математика", "department": "Кафедра ИТ", "hours": 144, "control_type": "Экзамен"},
            {"id": 2, "name": "Физика", "department": "Кафедра ИТ", "hours": 108, "control_type": "Экзамен"},
            {"id": 3, "name": "Программирование", "department": "Кафедра ИТ", "hours": 180, "control_type": "Экзамен"},
            {"id": 4, "name": "Базы данных", "department": "Кафедра ИТ", "hours": 72, "control_type": "Экзамен"},
            {"id": 5, "name": "Управление проектами", "department": "Кафедра ИТ", "hours": 72, "control_type": "Зачёт"},
            {"id": 6, "name": "Физическая культура", "department": "Кафедра физвоспитания", "hours": 72, "control_type": "Зачёт"},
        ]

# =====================================================
# ОСНОВНОЕ ПРИЛОЖЕНИЕ С ПОЛНЫМ RBAC/ACL
# =====================================================

class VirtualDeanApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Виртуальный деканат - Полная версия")
        self.root.state('zoomed')
        self.root.configure(bg=COLORS["bg"])
        
        # Инициализация компонентов
        self.data_manager = DataManager()
        self.acl_manager = ACLManager()
        self.role_hierarchy = RoleHierarchy()
        self.separation_duties = SeparationOfDuties()
        
        # Состояние сессии
        self.current_user = None
        self.current_role = None
        self.actions_taken = []  # для динамического разделения обязанностей
        self.user_data = None
        
        # Выбор метода аутентификации
        self.auth_method = "password"  # или "token"
        
        self.show_login()
    
    def show_login(self):
        """Окно входа с выбором метода аутентификации"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=COLORS["bg"])
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(main_frame, text="ВИРТУАЛЬНЫЙ ДЕКАНАТ", 
                font=("Segoe UI", 24, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=20)
        
        # Выбор метода аутентификации
        method_frame = tk.Frame(main_frame, bg=COLORS["bg"])
        method_frame.pack(pady=10)
        
        tk.Label(method_frame, text="Метод аутентификации:", font=("Segoe UI", 11),
                bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left", padx=5)
        
        self.auth_var = tk.StringVar(value="password")
        tk.Radiobutton(method_frame, text="Пароль", variable=self.auth_var, value="password",
                      bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["bg"],
                      command=lambda: self.switch_auth_method("password")).pack(side="left", padx=5)
        tk.Radiobutton(method_frame, text="Токен", variable=self.auth_var, value="token",
                      bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["bg"],
                      command=lambda: self.switch_auth_method("token")).pack(side="left", padx=5)
        
        # Форма входа
        self.login_frame = tk.Frame(main_frame, bg=COLORS["frame"], padx=40, pady=30)
        self.login_frame.pack(pady=20)
        
        self.update_login_form()
        
        self.root.mainloop()
    
    def switch_auth_method(self, method):
        self.auth_method = method
        self.update_login_form()
    
    def update_login_form(self):
        """Обновление формы в зависимости от метода аутентификации"""
        for widget in self.login_frame.winfo_children():
            widget.destroy()
        
        if self.auth_method == "password":
            tk.Label(self.login_frame, text="Логин", font=("Segoe UI", 12),
                    bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,5))
            self.login_entry = tk.Entry(self.login_frame, font=("Segoe UI", 13),
                                        bg=COLORS["bg"], fg=COLORS["text"], width=25)
            self.login_entry.pack(pady=(0,15))
            
            tk.Label(self.login_frame, text="Пароль", font=("Segoe UI", 12),
                    bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,5))
            self.password_entry = tk.Entry(self.login_frame, font=("Segoe UI", 13), show="•",
                                          bg=COLORS["bg"], fg=COLORS["text"], width=25)
            self.password_entry.pack(pady=(0,20))
            
            btn = tk.Button(self.login_frame, text="ВОЙТИ", font=("Segoe UI", 12, "bold"),
                           bg=COLORS["accent"], fg=COLORS["bg"], command=self.authenticate_password)
            btn.pack(fill="x", pady=10)
        else:
            tk.Label(self.login_frame, text="Токен доступа", font=("Segoe UI", 12),
                    bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,5))
            self.token_entry = tk.Entry(self.login_frame, font=("Segoe UI", 13),
                                        bg=COLORS["bg"], fg=COLORS["text"], width=25)
            self.token_entry.pack(pady=(0,20))
            
            btn = tk.Button(self.login_frame, text="ВОЙТИ ПО ТОКЕНУ", font=("Segoe UI", 12, "bold"),
                           bg=COLORS["accent"], fg=COLORS["bg"], command=self.authenticate_token)
            btn.pack(fill="x", pady=10)
        
        tk.Label(self.login_frame, text="Демо-токены: TOKEN_123, TOKEN_456, TOKEN_789",
                font=("Segoe UI", 8), bg=COLORS["frame"], fg=COLORS["subtext"]).pack(pady=(10,0))
    
    def authenticate_password(self):
        """Аутентификация по паролю"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        auth = PasswordAuthenticator()
        user_data = auth.authenticate(login, password)
        
        if user_data:
            self.current_user = login
            self.current_role = user_data["role"]
            self.user_data = user_data
            self.actions_taken = []
            self.show_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
    
    def authenticate_token(self):
        """Аутентификация по токену"""
        token = self.token_entry.get().strip()
        
        auth = TokenAuthenticator()
        user_data = auth.authenticate(token)
        
        if user_data:
            self.current_user = token
            self.current_role = user_data["role"]
            self.user_data = user_data
            self.actions_taken = []
            self.show_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный токен!")
    
    def show_main_interface(self):
        """Главный интерфейс после входа"""
        self.clear_window()
        
        # Проверка статического разделения обязанностей
        roles = [self.current_role]
        inherited = self.role_hierarchy.get_inherited_roles(self.current_role)
        roles.extend(inherited)
        
        is_valid, msg = self.separation_duties.check_static_separation(roles)
        if not is_valid:
            messagebox.showwarning("Предупреждение", f"Статическое разделение: {msg}")
        
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg=COLORS["frame"], height=60)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)
        
        info_text = f"{self.user_data['full_name']} | {self.current_role}"
        if self.auth_method == "token":
            info_text += " (Токен)"
        tk.Label(top_frame, text=info_text, font=("Segoe UI", 12),
                bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left", padx=25)
        
        tk.Button(top_frame, text="ВЫЙТИ", font=("Segoe UI", 11, "bold"),
                  bg=COLORS["error"], fg=COLORS["bg"], relief="flat", bd=0,
                  padx=20, pady=8, cursor="hand2", command=self.logout).pack(side="right", padx=25)
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg=COLORS["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Левая панель - меню на основе ACL
        left_panel = tk.Frame(main_container, bg=COLORS["frame"], width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="ДОСТУПНЫЕ ОБЪЕКТЫ", font=("Segoe UI", 12, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(20, 10))
        
        # Получаем объекты, к которым есть доступ
        available_objects = ["Schedule", "Grades", "Users", "Finance"]
        for obj in available_objects:
            perms = self.acl_manager.get_permissions(self.current_role, obj)
            if perms:
                obj_frame = tk.LabelFrame(left_panel, text=obj, font=("Segoe UI", 10, "bold"),
                                         bg=COLORS["frame"], fg=COLORS["subtext"])
                obj_frame.pack(fill="x", pady=5, padx=10)
                
                for perm in perms:
                    btn = tk.Button(obj_frame, text=perm.upper(), font=("Segoe UI", 10),
                                   bg=COLORS["button"], fg=COLORS["text"], relief="flat",
                                   padx=10, pady=5, cursor="hand2",
                                   command=lambda o=obj, p=perm: self.execute_action(o, p))
                    btn.pack(fill="x", pady=2, padx=5)
        
        # Правая панель - содержимое
        self.content_area = tk.Frame(main_container, bg=COLORS["frame"])
        self.content_area.pack(side="right", fill="both", expand=True)
        
        self.show_welcome()
    
    def execute_action(self, obj, action):
        """Выполнение действия с проверкой динамического разделения обязанностей"""
        # Проверка динамического разделения
        is_valid, msg = self.separation_duties.check_dynamic_separation(self.actions_taken, action)
        if not is_valid:
            messagebox.showerror("Ошибка", f"Динамическое разделение: {msg}")
            return
        
        # Выполнение действия
        if obj == "Schedule":
            if action == "read":
                self.show_schedule()
            else:
                self.show_placeholder(f"{obj} - {action}", "Функция в разработке")
        elif obj == "Grades":
            if action == "read":
                self.show_grades()
            else:
                self.show_placeholder(f"{obj} - {action}", "Функция в разработке")
        elif obj == "Users":
            if action == "read":
                self.show_users()
            else:
                self.show_placeholder(f"{obj} - {action}", "Функция в разработке")
        elif obj == "Finance":
            if action == "read_own_salary":
                self.show_salary()
            else:
                self.show_placeholder(f"{obj} - {action}", "Функция в разработке")
        
        # Добавляем действие в список выполненных для динамического разделения
        self.actions_taken.append(action)
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_welcome(self):
        self.clear_content()
        tk.Label(self.content_area, text=f"Добро пожаловать, {self.user_data['full_name']}!",
                font=("Segoe UI", 20, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=60)
        tk.Label(self.content_area, text=f"Роль: {self.current_role}",
                font=("Segoe UI", 13), bg=COLORS["frame"], fg=COLORS["subtext"]).pack()
        tk.Label(self.content_area, text=f"Метод аутентификации: {'Пароль' if self.auth_method == 'password' else 'Токен'}",
                font=("Segoe UI", 12), bg=COLORS["frame"], fg=COLORS["text"]).pack(pady=10)
    
    def show_schedule(self):
        """Показать расписание"""
        self.clear_content()
        
        tk.Label(self.content_area, text="РАСПИСАНИЕ ЗАНЯТИЙ", font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=10)
        
        notebook = ttk.Notebook(self.content_area)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        for day, lessons in self.data_manager.schedule.items():
            day_frame = tk.Frame(notebook, bg=COLORS["frame"])
            notebook.add(day_frame, text=day)
            
            # Таблица
            columns = ("pair", "time", "subject", "room", "teacher", "type", "format", "period")
            tree = ttk.Treeview(day_frame, columns=columns, show="headings", height=12)
            
            tree.heading("pair", text="Пара")
            tree.heading("time", text="Время")
            tree.heading("subject", text="Дисциплина")
            tree.heading("room", text="Ауд.")
            tree.heading("teacher", text="Преподаватель")
            tree.heading("type", text="Тип")
            tree.heading("format", text="Формат")
            tree.heading("period", text="Период")
            
            for col in columns:
                tree.column(col, width=100 if col != "subject" else 180, anchor="center")
            
            for lesson in lessons:
                format_icon = "● Очно" if lesson["format"] == "Очно" else "○ Дистант"
                tree.insert("", "end", values=(
                    lesson["pair"], lesson["time"], lesson["subject"], lesson["room"],
                    lesson["teacher"], lesson["type"], format_icon, lesson["period"]
                ))
            
            tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    def show_grades(self):
        """Показать успеваемость"""
        self.clear_content()
        
        tk.Label(self.content_area, text="МОДУЛЬНЫЙ ЖУРНАЛ", font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=10)
        
        student_name = self.user_data["full_name"]
        
        if student_name not in self.data_manager.grades:
            tk.Label(self.content_area, text="Данные об успеваемости не найдены",
                    font=("Segoe UI", 12), bg=COLORS["frame"], fg=COLORS["error"]).pack(pady=50)
            return
        
        # Выбор семестра
        semesters = list(self.data_manager.grades[student_name].keys())
        
        control_frame = tk.Frame(self.content_area, bg=COLORS["frame"])
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="Семестр:", font=("Segoe UI", 11),
                bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left", padx=5)
        
        semester_var = tk.StringVar(value=semesters[0])
        combo = ttk.Combobox(control_frame, textvariable=semester_var, values=semesters, state="readonly", width=15)
        combo.pack(side="left", padx=5)
        
        # Таблица
        columns = ("subject", "m1", "m2", "credit", "exam", "coefficient")
        tree = ttk.Treeview(self.content_area, columns=columns, show="headings", height=15)
        
        tree.heading("subject", text="ПРЕДМЕТ")
        tree.heading("m1", text="М1")
        tree.heading("m2", text="М2")
        tree.heading("credit", text="З")
        tree.heading("exam", text="Э")
        tree.heading("coefficient", text="К")
        
        tree.column("subject", width=250, anchor="w")
        for col in columns[1:]:
            tree.column(col, width=70, anchor="center")
        
        def load_grades(*args):
            for item in tree.get_children():
                tree.delete(item)
            
            semester = semester_var.get()
            grades = self.data_manager.grades[student_name].get(semester, [])
            
            total_weighted = 0
            total_coeff = 0
            
            for g in grades:
                m1 = g["m1"] if g["m1"] is not None else "—"
                m2 = g["m2"] if g["m2"] is not None else "—"
                credit = g["credit"] if g["credit"] is not None else "—"
                exam = g["exam"] if g["exam"] is not None else "—"
                coeff = g["coefficient"]
                
                tree.insert("", "end", values=(g["subject"], m1, m2, credit, exam, coeff))
                
                # Расчет рейтинга
                if g["credit"] is not None:
                    total_weighted += g["credit"] * coeff
                    total_coeff += coeff
                elif g["exam"] is not None and g["m1"] is not None and g["m2"] is not None:
                    avg = (g["m1"] + g["m2"] + g["exam"]) / 3
                    total_weighted += avg * coeff
                    total_coeff += coeff
            
            avg_rating = round(total_weighted / total_coeff, 1) if total_coeff > 0 else 0
            
            # Обновляем рейтинг
            for widget in self.content_area.winfo_children():
                if isinstance(widget, tk.Frame) and widget != control_frame and widget != tree.master:
                    widget.destroy()
            
            rating_frame = tk.Frame(self.content_area, bg=COLORS["frame"])
            rating_frame.pack(fill="x", pady=10, side="bottom")
            tk.Label(rating_frame, text=f"СРЕДНИЙ РЕЙТИНГ: {avg_rating}", font=("Segoe UI", 14, "bold"),
                    bg=COLORS["frame"], fg=COLORS["success"]).pack()
        
        combo.bind("<<ComboboxSelected>>", load_grades)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        load_grades()
    
    def show_users(self):
        """Показать список пользователей (доступно только с правами read)"""
        self.clear_content()
        
        tk.Label(self.content_area, text="УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ", font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=10)
        
        columns = ("login", "full_name", "role", "department")
        tree = ttk.Treeview(self.content_area, columns=columns, show="headings", height=15)
        
        tree.heading("login", text="Логин")
        tree.heading("full_name", text="ФИО")
        tree.heading("role", text="Роль")
        tree.heading("department", text="Подразделение")
        
        for col in columns:
            tree.column(col, width=200, anchor="w")
        
        for login, data in self.data_manager.users.items():
            dept = data.get("department", data.get("group", "—"))
            tree.insert("", "end", values=(login, data["full_name"], data["role"], dept))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_salary(self):
        """Показать зарплату (доступно преподавателю)"""
        self.clear_content()
        
        tk.Label(self.content_area, text="ЗАРПЛАТНАЯ ВЕДОМОСТЬ", font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=10)
        
        # Демо-данные
        salaries = {
            "Иванов В.В.": 85000,
            "Петрова А.С.": 75000,
            "Сидоров И.И.": 90000,
            "Смирнова Е.А.": 65000,
        }
        
        salary = salaries.get(self.user_data["full_name"], 50000)
        
        info_frame = tk.Frame(self.content_area, bg=COLORS["frame"], padx=30, pady=30)
        info_frame.pack(pady=50)
        
        tk.Label(info_frame, text=f"Сотрудник: {self.user_data['full_name']}", font=("Segoe UI", 14),
                bg=COLORS["frame"], fg=COLORS["text"]).pack(pady=10)
        tk.Label(info_frame, text=f"Должность: {self.user_data.get('position', 'Преподаватель')}", font=("Segoe UI", 14),
                bg=COLORS["frame"], fg=COLORS["text"]).pack(pady=10)
        tk.Label(info_frame, text=f"Заработная плата: {salary} руб.", font=("Segoe UI", 16, "bold"),
                bg=COLORS["frame"], fg=COLORS["success"]).pack(pady=10)
    
    def show_placeholder(self, title, message):
        self.clear_content()
        tk.Label(self.content_area, text=title, font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=30)
        tk.Label(self.content_area, text=message, font=("Segoe UI", 12),
                bg=COLORS["frame"], fg=COLORS["text"]).pack(pady=20)
    
    def logout(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.show_login()
    
    def run(self):
        self.root.mainloop()

# =====================================================
# ЗАПУСК
# =====================================================

# Цветовая схема
COLORS = {
    "bg": "#1e1e2e",
    "frame": "#2a2a3e",
    "button": "#4a4a6a",
    "accent": "#89b4fa",
    "text": "#cdd6f4",
    "subtext": "#a6adc8",
    "success": "#a6e3a1",
    "error": "#f38ba8",
}

if __name__ == "__main__":
    app = VirtualDeanApp()
    app.run()

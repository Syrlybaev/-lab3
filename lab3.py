# =====================================================
# ЛАБОРАТОРНАЯ РАБОТА №3 (ФИНАЛЬНАЯ ВЕРСИЯ)
# Студент: Слисаренко Дарья
# =====================================================

import tkinter as tk
from tkinter import messagebox, ttk

# -----------------------------------------------------
# ЦВЕТА
# -----------------------------------------------------
COLORS = {
    "bg": "#1e1e2e",
    "frame": "#2a2a3e",
    "button": "#4a4a6a",
    "button_hover": "#6a6a8a",
    "accent": "#89b4fa",
    "text": "#cdd6f4",
    "subtext": "#a6adc8",
    "success": "#a6e3a1",
    "warning": "#f9e2af",
    "error": "#f38ba8",
    "online_bg": "#2a4a3a",
    "online_text": "#94e2d5",
    "offline_bg": "#4a2a5a",
    "offline_text": "#cba6f7",
}

# -----------------------------------------------------
# ПОЛЬЗОВАТЕЛИ
# -----------------------------------------------------
USERS = {
    "dispetcher": {"password": "123", "role": "Диспетчерская служба", "full_name": "Петрова А.С."},
    "zav_kaf": {"password": "456", "role": "Заведующий кафедрой", "full_name": "Сидоров И.И."},
    "teacher": {"password": "789", "role": "Преподаватель", "full_name": "Иванов В.В."},
    "student": {"password": "000", "role": "Студент", "full_name": "Смирнова Е.А."}
}

# -----------------------------------------------------
# ACL
# -----------------------------------------------------
ACL = {
    "Диспетчерская служба": [
        "Просмотр расписания", "Редактирование расписания", "Публикация расписания",
        "Просмотр отчётов", "Управление заменами"
    ],
    "Заведующий кафедрой": [
        "Просмотр расписания", "Согласование расписания", "Отправка замечаний", "Просмотр отчётов"
    ],
    "Преподаватель": [
        "Просмотр расписания", "Подача заявки на замену"
    ],
    "Студент": [
        "Просмотр расписания", "Просмотр успеваемости"
    ]
}

# -----------------------------------------------------
# ВРЕМЯ ПАР
# -----------------------------------------------------
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

# -----------------------------------------------------
# РАСПИСАНИЕ (с ЛАБОРАТОРНЫМИ работами)
# -----------------------------------------------------
SCHEDULE_DATA = [
    # ПОНЕДЕЛЬНИК
    {"day": "Понедельник", "date": "07.04", "pair": 1, "time": PAIR_TIMES[1], 
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Математика", "room": "0211", "teacher": "Проф. Иванов", "type": "Лекция", "format": "Очно"},
    {"day": "Понедельник", "date": "07.04", "pair": 2, "time": PAIR_TIMES[2], 
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Физика", "room": "0304", "teacher": "Доц. Петров", "type": "Лабораторная", "format": "Очно"},
    {"day": "Понедельник", "date": "07.04", "pair": 3, "time": PAIR_TIMES[3], 
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Английский язык", "room": "401", "teacher": "Ст. Денисова", "type": "Семинар", "format": "Очно"},
    
    # ВТОРНИК
    {"day": "Вторник", "date": "08.04", "pair": 1, "time": PAIR_TIMES[1], 
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Программирование", "room": "0211", "teacher": "Проф. Сидоров", "type": "Лекция", "format": "Дистант"},
    {"day": "Вторник", "date": "08.04", "pair": 3, "time": PAIR_TIMES[3], 
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Базы данных", "room": "401", "teacher": "Доц. Смирнова", "type": "Лабораторная", "format": "Очно"},
    {"day": "Вторник", "date": "08.04", "pair": 4, "time": PAIR_TIMES[4], 
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Web-технологии", "room": "0304", "teacher": "Проф. Козлов", "type": "Семинар", "format": "Очно"},
    
    # СРЕДА
    {"day": "Среда", "date": "09.04", "pair": 1, "time": PAIR_TIMES[1], 
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Компьютерные сети", "room": "0211", "teacher": "Доц. Воробьёва", "type": "Лекция", "format": "Очно"},
    {"day": "Среда", "date": "09.04", "pair": 3, "time": PAIR_TIMES[3], 
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Информационная безопасность", "room": "401", "teacher": "Проф. Соколов", "type": "Лабораторная", "format": "Очно"},
    {"day": "Среда", "date": "09.04", "pair": 5, "time": PAIR_TIMES[5], 
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Операционные системы", "room": "0304", "teacher": "Проф. Новиков", "type": "Семинар", "format": "Дистант"},
    
    # ЧЕТВЕРГ
    {"day": "Четверг", "date": "10.04", "pair": 2, "time": PAIR_TIMES[2], 
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Дискретная математика", "room": "0211", "teacher": "Доц. Морозова", "type": "Лекция", "format": "Очно"},
    {"day": "Четверг", "date": "10.04", "pair": 4, "time": PAIR_TIMES[4], 
     "period_start": "19.02", "period_end": "12.03",
     "subject": "Экономика", "room": "401", "teacher": "Доц. Лебедева", "type": "Семинар", "format": "Очно"},
    {"day": "Четверг", "date": "10.04", "pair": 5, "time": PAIR_TIMES[5], 
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Методология науки", "room": "0211", "teacher": "Проф. Андреев", "type": "Лекция", "format": "Очно"},
    
    # ПЯТНИЦА
    {"day": "Пятница", "date": "11.04", "pair": 1, "time": PAIR_TIMES[1], 
     "period_start": "10.02", "period_end": "14.04",
     "subject": "Машинное обучение", "room": "0211", "teacher": "Проф. Орлов", "type": "Лекция", "format": "Дистант"},
    {"day": "Пятница", "date": "11.04", "pair": 4, "time": PAIR_TIMES[4], 
     "period_start": "27.02", "period_end": "10.04",
     "subject": "Анализ данных", "room": "0304", "teacher": "Доц. Крылова", "type": "Лабораторная", "format": "Очно"},
    
    # СУББОТА
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

# -----------------------------------------------------
# УСПЕВАЕМОСТЬ (экзамены и зачёты чередуются, баллы в З до 54)
# -----------------------------------------------------
GRADES_DATA = {
    "2025 - осень": [
        {"subject": "Математика", "m1": 38, "m2": 42, "exam": 40, "credit": None, "coefficient": 2.5},
        {"subject": "Физика", "m1": 35, "m2": 36, "exam": None, "credit": 48, "coefficient": 2.0},
        {"subject": "Программирование", "m1": 45, "m2": 48, "exam": 50, "credit": None, "coefficient": 3.0},
    ],
    "2026 - весна": [
        # Экзамены
        {"subject": "Информационные системы", "m1": 42, "m2": 48, "exam": 50, "credit": None, "coefficient": 2.8},
        {"subject": "Базы данных", "m1": 38, "m2": 40, "exam": 45, "credit": None, "coefficient": 2.5},
        # Зачёт с баллом
        {"subject": "Web-технологии", "m1": 35, "m2": 38, "exam": None, "credit": 42, "coefficient": 2.2},
        # Экзамен
        {"subject": "Машинное обучение", "m1": 40, "m2": 42, "exam": 48, "credit": None, "coefficient": 3.0},
        # Зачёт с баллом
        {"subject": "Анализ данных", "m1": 36, "m2": 39, "exam": None, "credit": 44, "coefficient": 2.6},
        # Зачёт с баллом
        {"subject": "Управление проектами", "m1": 32, "m2": 35, "exam": None, "credit": 38, "coefficient": 1.5},
        # Зачёт (с баллами в М1 и М2)
        {"subject": "Физическая культура", "m1": 40, "m2": 42, "exam": None, "credit": 45, "coefficient": 1.0},
        # Экзамен
        {"subject": "Компьютерные сети", "m1": 41, "m2": 43, "exam": 46, "credit": None, "coefficient": 2.7},
        # Зачёт с баллом
        {"subject": "Операционные системы", "m1": 33, "m2": 36, "exam": None, "credit": 40, "coefficient": 2.4},
        # Зачёт с баллом
        {"subject": "Психология", "m1": 40, "m2": 42, "exam": None, "credit": 48, "coefficient": 1.8},
        # Экзамен
        {"subject": "Методология науки", "m1": 44, "m2": 45, "exam": 49, "credit": None, "coefficient": 2.9},
    ],
    "2026 - осень": [
        {"subject": "Риторика", "m1": 38, "m2": 40, "exam": None, "credit": 42, "coefficient": 1.2},
        {"subject": "Правоведение", "m1": 35, "m2": 37, "exam": 41, "credit": None, "coefficient": 2.1},
        {"subject": "Дипломное проектирование", "m1": None, "m2": None, "exam": None, "credit": 50, "coefficient": 0.8},
    ],
}

# -----------------------------------------------------
# ОКНО ВХОДА
# -----------------------------------------------------
class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Виртуальный деканат - Вход")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        self.root.configure(bg=COLORS["bg"])
        
        self.create_widgets()
    
    def create_widgets(self):
        center_frame = tk.Frame(self.root, bg=COLORS["frame"], bd=0)
        center_frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=380)
        
        title = tk.Label(center_frame, text="ВИРТУАЛЬНЫЙ ДЕКАНАТ", 
                         font=("Segoe UI", 22, "bold"), bg=COLORS["frame"], fg=COLORS["accent"])
        title.pack(pady=35)
        
        login_frame = tk.Frame(center_frame, bg=COLORS["frame"])
        login_frame.pack(pady=25, padx=50, fill="both", expand=True)
        
        tk.Label(login_frame, text="Логин", font=("Segoe UI", 12), 
                bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,5))
        self.login_entry = tk.Entry(login_frame, font=("Segoe UI", 13), 
                                     bg=COLORS["bg"], fg=COLORS["text"],
                                     insertbackground=COLORS["accent"],
                                     relief="flat", bd=0, highlightthickness=2,
                                     highlightcolor=COLORS["accent"], highlightbackground=COLORS["subtext"])
        self.login_entry.pack(fill="x", pady=(0,20))
        
        tk.Label(login_frame, text="Пароль", font=("Segoe UI", 12), 
                bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0,5))
        self.password_entry = tk.Entry(login_frame, font=("Segoe UI", 13), show="•",
                                       bg=COLORS["bg"], fg=COLORS["text"],
                                       insertbackground=COLORS["accent"],
                                       relief="flat", bd=0, highlightthickness=2,
                                       highlightcolor=COLORS["accent"], highlightbackground=COLORS["subtext"])
        self.password_entry.pack(fill="x", pady=(0,30))
        
        login_btn = tk.Button(login_frame, text="ВОЙТИ В СИСТЕМУ", font=("Segoe UI", 14, "bold"),
                              bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", bd=0,
                              padx=40, pady=15, cursor="hand2", command=self.authenticate)
        login_btn.pack(fill="x", pady=15, ipady=5)
        
        self.root.bind('<Return>', lambda event: self.authenticate())
    
    def authenticate(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if login in USERS and USERS[login]["password"] == password:
            self.root.destroy()
            self.on_login_success(login, USERS[login]["role"], USERS[login]["full_name"])
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
            self.login_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

# -----------------------------------------------------
# ГЛАВНОЕ ОКНО
# -----------------------------------------------------
class MainApp:
    def __init__(self, login, role, full_name):
        self.root = tk.Tk()
        self.root.title("Виртуальный деканат")
        self.root.state('zoomed')
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        self.root.configure(bg=COLORS["bg"])
        
        self.current_user = login
        self.current_role = role
        self.full_name = full_name
        self.current_semester = "2026 - весна"
        
        self.create_widgets()
    
    def create_widgets(self):
        top_frame = tk.Frame(self.root, bg=COLORS["frame"], height=55)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)
        
        user_text = f"{self.full_name} | {self.current_role}"
        tk.Label(top_frame, text=user_text, font=("Segoe UI", 12),
                bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left", padx=25)
        
        tk.Button(top_frame, text="ВЫЙТИ", font=("Segoe UI", 11, "bold"),
                  bg=COLORS["error"], fg=COLORS["bg"], relief="flat", bd=0,
                  padx=20, pady=8, cursor="hand2", command=self.logout).pack(side="right", padx=25)
        
        main_frame = tk.Frame(self.root, bg=COLORS["bg"])
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        left_frame = tk.Frame(main_frame, bg=COLORS["frame"], width=280)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="ДОСТУПНЫЕ ДЕЙСТВИЯ", font=("Segoe UI", 12, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(25, 20))
        
        for action in ACL.get(self.current_role, []):
            btn = tk.Button(left_frame, text=action, font=("Segoe UI", 11),
                           bg=COLORS["button"], fg=COLORS["text"], relief="flat", bd=0,
                           padx=12, pady=10, activebackground=COLORS["button_hover"],
                           cursor="hand2", command=lambda a=action: self.execute_action(a))
            btn.pack(pady=6, padx=15, fill="x")
        
        self.output_area = tk.Frame(main_frame, bg=COLORS["frame"])
        self.output_area.pack(side="right", fill="both", expand=True)
        
        self.show_welcome()
    
    def clear_output(self):
        for widget in self.output_area.winfo_children():
            widget.destroy()
    
    def show_welcome(self):
        self.clear_output()
        tk.Label(self.output_area, text=f"Добро пожаловать, {self.full_name}!",
                font=("Segoe UI", 20, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=60)
        tk.Label(self.output_area, text="Выберите действие из меню слева",
                font=("Segoe UI", 13), bg=COLORS["frame"], fg=COLORS["subtext"]).pack()
    
    def show_schedule(self):
        """Расписание с ровной таблицей"""
        self.clear_output()
        
        tk.Label(self.output_area, text="РАСПИСАНИЕ ЗАНЯТИЙ", font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(10, 5))
        
        # Контейнер с прокруткой
        container = tk.Frame(self.output_area, bg=COLORS["frame"])
        container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(container, bg=COLORS["frame"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["frame"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Функция для создания ровной таблицы
        def create_table(parent, headers, data_rows):
            # Заголовки
            header_frame = tk.Frame(parent, bg=COLORS["button"])
            header_frame.pack(fill="x", pady=(0, 2))
            
            col_widths = [50, 100, 100, 180, 70, 180, 110, 90]
            for i, (header, width) in enumerate(zip(headers, col_widths)):
                tk.Label(header_frame, text=header, font=("Segoe UI", 9, "bold"),
                        bg=COLORS["button"], fg=COLORS["text"], width=width//7, 
                        anchor="center", padx=4, pady=4).grid(row=0, column=i, sticky="nsew")
                header_frame.grid_columnconfigure(i, weight=1)
            
            # Данные
            for row_data in data_rows:
                row_bg = COLORS["online_bg"] if row_data[7] == "● Очно" else COLORS["offline_bg"]
                text_color = COLORS["online_text"] if row_data[7] == "● Очно" else COLORS["offline_text"]
                
                row_frame = tk.Frame(parent, bg=row_bg)
                row_frame.pack(fill="x", pady=1)
                
                for i, (val, width) in enumerate(zip(row_data, col_widths)):
                    tk.Label(row_frame, text=val, font=("Segoe UI", 9),
                            bg=row_bg, fg=text_color, width=width//7,
                            anchor="center", padx=4, pady=4).grid(row=0, column=i, sticky="nsew")
                    row_frame.grid_columnconfigure(i, weight=1)
        
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        headers = ["Пара", "Время", "Период", "Дисциплина", "Ауд.", "Преподаватель", "Тип", "Формат"]
        
        for day in days:
            day_schedule = [item for item in SCHEDULE_DATA if item["day"] == day]
            if day_schedule:
                day_frame = tk.LabelFrame(scrollable_frame, text=day, font=("Segoe UI", 13, "bold"),
                                          bg=COLORS["frame"], fg=COLORS["accent"], bd=2, relief="groove")
                day_frame.pack(fill="x", pady=12, padx=12)
                
                data_rows = []
                for item in sorted(day_schedule, key=lambda x: x["pair"]):
                    format_text = "● Очно" if item["format"] == "Очно" else "○ Дистант"
                    period = f"{item['period_start']}-{item['period_end']}"
                    row = [str(item["pair"]), item["time"], period, item["subject"], 
                           item["room"], item["teacher"], item["type"], format_text]
                    data_rows.append(row)
                
                create_table(day_frame, headers, data_rows)
    
    def show_grades(self):
        """Успеваемость: колонки М1, М2, З (баллы), Э (баллы), К"""
        self.clear_output()
        
        tk.Label(self.output_area, text="МОДУЛЬНЫЙ ЖУРНАЛ", font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(10, 5))
        
        # Выбор семестра
        semester_frame = tk.Frame(self.output_area, bg=COLORS["frame"])
        semester_frame.pack(pady=(5, 15))
        tk.Label(semester_frame, text="Семестр:", font=("Segoe UI", 11),
                bg=COLORS["frame"], fg=COLORS["subtext"]).pack(side="left", padx=5)
        
        self.semester_var = tk.StringVar(value=self.current_semester)
        semester_combo = ttk.Combobox(semester_frame, textvariable=self.semester_var, 
                                       values=list(GRADES_DATA.keys()),
                                       state="readonly", width=15, font=("Segoe UI", 10))
        semester_combo.pack(side="left", padx=5)
        semester_combo.bind("<<ComboboxSelected>>", lambda e: self.load_grades())
        
        # Таблица с колонками: Предмет, М1, М2, З, Э, К
        columns = ("subject", "m1", "m2", "credit", "exam", "coefficient")
        tree = ttk.Treeview(self.output_area, columns=columns, show="headings", height=15)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLORS["bg"], foreground=COLORS["text"],
                       fieldbackground=COLORS["bg"], font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=COLORS["button"], foreground=COLORS["text"],
                       font=("Segoe UI", 10, "bold"))
        
        tree.heading("subject", text="ПРЕДМЕТ")
        tree.heading("m1", text="М1")
        tree.heading("m2", text="М2")
        tree.heading("credit", text="З")
        tree.heading("exam", text="Э")
        tree.heading("coefficient", text="К")
        
        tree.column("subject", width=320, anchor="w")
        tree.column("m1", width=60, anchor="center")
        tree.column("m2", width=60, anchor="center")
        tree.column("credit", width=80, anchor="center")
        tree.column("exam", width=80, anchor="center")
        tree.column("coefficient", width=80, anchor="center")
        
        self.grades_tree = tree
        self.load_grades()
        
        tree.pack(fill="both", expand=True, pady=(0, 15))
    
    def load_grades(self):
        """Загрузка данных: З - баллы за зачёт, Э - баллы за экзамен"""
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        
        semester = self.semester_var.get()
        semester_data = GRADES_DATA.get(semester, [])
        
        total_weighted = 0
        total_coeff = 0
        
        for item in semester_data:
            m1_val = item["m1"] if item["m1"] is not None else "—"
            m2_val = item["m2"] if item["m2"] is not None else "—"
            
            # З (зачёт) - показываем баллы
            if item["credit"] is not None:
                credit_val = str(item["credit"])
                total_weighted += item["credit"] * item["coefficient"]
                total_coeff += item["coefficient"]
            else:
                credit_val = "—"
            
            # Э (экзамен) - показываем баллы или "—"
            if item["exam"] is not None:
                exam_val = str(item["exam"])
                if item["m1"] is not None and item["m2"] is not None:
                    avg_exam = (item["m1"] + item["m2"] + item["exam"]) / 3
                    total_weighted += avg_exam * item["coefficient"]
                    total_coeff += item["coefficient"]
            else:
                exam_val = "—"
            
            coeff_val = f"{item['coefficient']:.1f}"
            
            self.grades_tree.insert("", "end", values=(
                item["subject"], m1_val, m2_val, credit_val, exam_val, coeff_val
            ))
        
        # Средний рейтинг внизу (без подписи "с учётом К")
        avg_rating = round(total_weighted / total_coeff, 1) if total_coeff > 0 else 0
        
        # Удаляем старый фрейм рейтинга
        for widget in self.output_area.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.grades_tree.master:
                if widget.winfo_children() and isinstance(widget.winfo_children()[0], tk.Label):
                    if "СРЕДНИЙ РЕЙТИНГ" in widget.winfo_children()[0].cget("text"):
                        widget.destroy()
        
        rating_frame = tk.Frame(self.output_area, bg=COLORS["frame"])
        rating_frame.pack(fill="x", pady=15, side="bottom")
        tk.Label(rating_frame, text=f"СРЕДНИЙ РЕЙТИНГ: {avg_rating}", font=("Segoe UI", 14, "bold"),
                bg=COLORS["frame"], fg=COLORS["success"]).pack()
    
    def execute_action(self, action):
        if action == "Просмотр расписания":
            self.show_schedule()
        elif action == "Просмотр успеваемости":
            self.show_grades()
        else:
            self.show_placeholder(action, "Функция в разработке")
    
    def show_placeholder(self, title_text, content_text):
        self.clear_output()
        tk.Label(self.output_area, text=title_text, font=("Segoe UI", 18, "bold"),
                bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(30, 20))
        tk.Label(self.output_area, text=content_text, font=("Segoe UI", 12),
                bg=COLORS["frame"], fg=COLORS["text"]).pack()
    
    def logout(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()
            new_root = tk.Tk()
            LoginWindow(new_root, start_main_app)
            new_root.mainloop()
    
    def run(self):
        self.root.mainloop()

# -----------------------------------------------------
# ЗАПУСК
# -----------------------------------------------------
def start_main_app(login, role, full_name):
    app = MainApp(login, role, full_name)
    app.run()

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, start_main_app)
    root.mainloop()
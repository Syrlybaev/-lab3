from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from modules.finance_module import FinanceModule
from modules.grades_module import GradesModule
from modules.schedule_module import ScheduleModule
from modules.teachers_module import TeachersModule
from modules.users_module import UsersModule
from services.auth import AuthService, SessionUser
from services.rbac import RBACService
from ui.theme import COLORS, FONT, WINDOW_TITLE


class LoginWindow:
    def __init__(self, root: tk.Tk, on_login_success) -> None:
        self.root = root
        self.on_login_success = on_login_success
        self.auth_service = AuthService()
        self.auth_method = tk.StringVar(value="password")
        self.root.title(f"{WINDOW_TITLE} - Вход")
        self.root.geometry("620x560")
        self.root.minsize(540, 430)
        self.root.configure(bg=COLORS["bg"])
        self.form_frame: tk.Frame | None = None
        self.login_entry: tk.Entry | None = None
        self.password_entry: tk.Entry | None = None
        self.token_entry: tk.Entry | None = None
        self.create_widgets()

    def create_widgets(self) -> None:
        center_frame = tk.Frame(self.root, bg=COLORS["frame"], bd=0)
        center_frame.place(relx=0.5, rely=0.5, anchor="center", width=470, height=430)
        tk.Label(center_frame, text="ВИРТУАЛЬНЫЙ ДЕКАНАТ", font=(FONT, 22, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(28, 8))
        tk.Label(center_frame, text="Единое приложение команды. Основной вариант лабы: вход по постоянному паролю.", font=(FONT, 10), bg=COLORS["frame"], fg=COLORS["subtext"], wraplength=360).pack(pady=(0, 8))

        switch = tk.Frame(center_frame, bg=COLORS["frame"])
        switch.pack(pady=(5, 15))
        tk.Label(switch, text="Метод входа:", font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left", padx=(0, 8))
        tk.Radiobutton(switch, text="Пароль", variable=self.auth_method, value="password", command=self.render_form, bg=COLORS["frame"], fg=COLORS["text"], selectcolor=COLORS["frame"], activebackground=COLORS["frame"]).pack(side="left", padx=8)
        tk.Radiobutton(switch, text="Токен", variable=self.auth_method, value="token", command=self.render_form, bg=COLORS["frame"], fg=COLORS["text"], selectcolor=COLORS["frame"], activebackground=COLORS["frame"]).pack(side="left", padx=8)

        self.form_frame = tk.Frame(center_frame, bg=COLORS["frame"])
        self.form_frame.pack(padx=50, fill="both", expand=True)
        self.render_form()
        self.root.bind("<Return>", lambda _event: self.authenticate())

    def render_form(self) -> None:
        assert self.form_frame is not None
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.login_entry = None
        self.password_entry = None
        self.token_entry = None

        if self.auth_method.get() == "password":
            tk.Label(self.form_frame, text="Логин", font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(5, 5))
            self.login_entry = tk.Entry(self.form_frame, font=(FONT, 13), bg=COLORS["bg"], fg=COLORS["text"], insertbackground=COLORS["accent"], relief="flat", bd=0, highlightthickness=2, highlightcolor=COLORS["accent"], highlightbackground=COLORS["subtext"])
            self.login_entry.pack(fill="x", pady=(0, 20))
            tk.Label(self.form_frame, text="Пароль", font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(0, 5))
            self.password_entry = tk.Entry(self.form_frame, font=(FONT, 13), show="•", bg=COLORS["bg"], fg=COLORS["text"], insertbackground=COLORS["accent"], relief="flat", bd=0, highlightthickness=2, highlightcolor=COLORS["accent"], highlightbackground=COLORS["subtext"])
            self.password_entry.pack(fill="x", pady=(0, 20))
            hint = "Логины: dispetcher / zav_kaf / teacher / student / methodist / accountant / dean_admin"
        else:
            tk.Label(self.form_frame, text="Токен доступа", font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(5, 5))
            self.token_entry = tk.Entry(self.form_frame, font=(FONT, 13), bg=COLORS["bg"], fg=COLORS["text"], insertbackground=COLORS["accent"], relief="flat", bd=0, highlightthickness=2, highlightcolor=COLORS["accent"], highlightbackground=COLORS["subtext"])
            self.token_entry.pack(fill="x", pady=(0, 20))
            hint = "Токены: TOKEN_123 / TOKEN_456 / TOKEN_789"

        tk.Label(self.form_frame, text=hint, font=(FONT, 9), bg=COLORS["frame"], fg=COLORS["subtext"], wraplength=320).pack(pady=(0, 15))
        tk.Button(self.form_frame, text="ВОЙТИ В СИСТЕМУ", font=(FONT, 14, "bold"), bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", bd=0, padx=40, pady=15, cursor="hand2", command=self.authenticate).pack(fill="x", pady=10, ipady=5)

    def authenticate(self) -> None:
        if self.auth_method.get() == "password":
            login = self.login_entry.get().strip() if self.login_entry else ""
            password = self.password_entry.get().strip() if self.password_entry else ""
            user = self.auth_service.authenticate_password(login, password)
        else:
            token = self.token_entry.get().strip() if self.token_entry else ""
            user = self.auth_service.authenticate_token(token)
        if user is None:
            messagebox.showerror("Ошибка", "Неверные учетные данные")
            return
        self.root.destroy()
        self.on_login_success(user)


class MainApp:
    def __init__(self, current_user: SessionUser) -> None:
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.state("zoomed")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        self.root.configure(bg=COLORS["bg"])
        self.current_user = current_user
        self.rbac = RBACService()
        self.current_semester = "2026 - весна"
        self.output_area: tk.Frame | None = None
        self.schedule_module: ScheduleModule | None = None
        self.grades_module: GradesModule | None = None
        self.teachers_module: TeachersModule | None = None
        self.users_module: UsersModule | None = None
        self.finance_module: FinanceModule | None = None
        self.create_widgets()

    def create_widgets(self) -> None:
        top_frame = tk.Frame(self.root, bg=COLORS["frame"], height=55)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)
        auth_name = "пароль" if self.current_user.auth_method == "password" else "токен"
        user_text = f"{self.current_user.full_name} | {self.rbac.role_titles(self.current_user.roles)} | вход: {auth_name}"
        tk.Label(top_frame, text=user_text, font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left", padx=25)
        tk.Button(top_frame, text="ВЫЙТИ", font=(FONT, 11, "bold"), bg=COLORS["error"], fg=COLORS["bg"], relief="flat", bd=0, padx=20, pady=8, cursor="hand2", command=self.logout).pack(side="right", padx=25)

        main_frame = tk.Frame(self.root, bg=COLORS["bg"])
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        left_frame = tk.Frame(main_frame, bg=COLORS["frame"], width=310)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)
        tk.Label(left_frame, text="ДОСТУПНЫЕ ДЕЙСТВИЯ", font=(FONT, 12, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(25, 20))

        for item in self.rbac.allowed_menu(self.current_user.roles):
            title = item["title"]
            tk.Button(left_frame, text=title, font=(FONT, 11), bg=COLORS["button"], fg=COLORS["text"], relief="flat", bd=0, padx=12, pady=10, activebackground=COLORS["button_hover"], cursor="hand2", command=lambda action=title: self.execute_action(action)).pack(pady=6, padx=15, fill="x")

        rights_frame = tk.Frame(left_frame, bg=COLORS["frame"])
        rights_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        tk.Label(rights_frame, text="Выбранные варианты лабы", font=(FONT, 10, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(anchor="w")
        summary = "Ч.1: постоянный пароль\nЧ.2: ACL\nЧ.3: иерархическое RBAC"
        tk.Label(rights_frame, text=summary, justify="left", font=(FONT, 9), bg=COLORS["frame"], fg=COLORS["subtext"]).pack(anchor="w", pady=(6, 0))

        self.output_area = tk.Frame(main_frame, bg=COLORS["frame"])
        self.output_area.pack(side="right", fill="both", expand=True)
        self.schedule_module = ScheduleModule(self.output_area)
        self.grades_module = GradesModule(self.output_area, current_user=self.current_user, current_semester=self.current_semester)
        self.teachers_module = TeachersModule(self.output_area, self.current_user, self.rbac)
        self.users_module = UsersModule(self.output_area)
        self.finance_module = FinanceModule(self.output_area, self.current_user)
        self.show_welcome()

    def clear_output(self) -> None:
        assert self.output_area is not None
        for widget in self.output_area.winfo_children():
            widget.destroy()

    def show_welcome(self) -> None:
        self.clear_output()
        tk.Label(self.output_area, text=f"Добро пожаловать, {self.current_user.full_name}!", font=(FONT, 20, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=45)
        info = tk.Frame(self.output_area, bg=COLORS["bg"])
        info.pack(padx=25, pady=15, fill="x")
        intro = (
            "Объединённая версия проекта собрана из модульной архитектуры и функционала версии одногруппницы.\n"
            "Сохранены расписание, успеваемость и роли; добавлен модуль преподавателей и служебные экраны."
        )
        tk.Label(info, text=intro, justify="left", font=(FONT, 11), bg=COLORS["bg"], fg=COLORS["text"], wraplength=850).pack(anchor="w", padx=18, pady=(18, 8))
        permissions = self.rbac.explain_permissions(self.current_user.roles)
        lines = [f"• {resource}: {', '.join(actions)}" for resource, actions in permissions.items()]
        tk.Label(info, text="Ваши права:\n" + "\n".join(lines), justify="left", font=(FONT, 10), bg=COLORS["bg"], fg=COLORS["subtext"], wraplength=850).pack(anchor="w", padx=18, pady=(0, 18))

    def execute_action(self, action: str) -> None:
        if action == "Просмотр расписания":
            self.schedule_module.render()
        elif action == "Просмотр успеваемости":
            self.grades_module.render()
        elif action == "Преподаватели":
            self.teachers_module.render()
        elif action == "Пользователи":
            self.users_module.render()
        elif action == "Моя зарплата":
            self.finance_module.render_salary()
        elif action == "Финансы":
            self.finance_module.render_finance_overview()
        else:
            self.schedule_module.render_stub(action, "Функционал сохранён в общем меню и может быть развит командой без изменения архитектуры проекта.")

    def logout(self) -> None:
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()
            new_root = tk.Tk()
            LoginWindow(new_root, start_main_app)
            new_root.mainloop()

    def run(self) -> None:
        self.root.mainloop()


def start_main_app(user: SessionUser) -> None:
    app = MainApp(user)
    app.run()


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, start_main_app)
    root.mainloop()

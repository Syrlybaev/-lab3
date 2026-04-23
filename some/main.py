from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from modules.finance_module import FinanceModule
from modules.grades_module import GradesModule
from modules.schedule_module import ScheduleModule
from modules.students_module import StudentsModule
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
        self.login_entry: tk.Entry | None = None
        self.password_entry: tk.Entry | None = None
        self.root.title(f"{WINDOW_TITLE} — Вход")
        self.root.geometry("720x520")
        self.root.minsize(640, 480)
        self.root.configure(bg=COLORS["bg"])
        self._create_widgets()

    def _create_widgets(self) -> None:
        card = tk.Frame(
            self.root, bg=COLORS["frame"], bd=0,
            highlightthickness=1, highlightbackground=COLORS["line"],
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=480, height=340)

        tk.Label(
            card, text="ВИРТУАЛЬНЫЙ ДЕКАНАТ",
            font=(FONT, 22, "bold"), bg=COLORS["frame"], fg=COLORS["accent"],
        ).pack(pady=(32, 20))

        form = tk.Frame(card, bg=COLORS["frame"])
        form.pack(fill="x", padx=52)

        tk.Label(form, text="Логин", font=(FONT, 12),
                 bg=COLORS["frame"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        self.login_entry = tk.Entry(
            form, font=(FONT, 13), bg=COLORS["bg"], fg=COLORS["text"],
            insertbackground=COLORS["accent"], relief="flat",
            highlightthickness=2, highlightbackground=COLORS["line"], highlightcolor=COLORS["accent"],
        )
        self.login_entry.pack(fill="x", pady=(0, 16))

        tk.Label(form, text="Пароль", font=(FONT, 12),
                 bg=COLORS["frame"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        self.password_entry = tk.Entry(
            form, show="*", font=(FONT, 13), bg=COLORS["bg"], fg=COLORS["text"],
            insertbackground=COLORS["accent"], relief="flat",
            highlightthickness=2, highlightbackground=COLORS["line"], highlightcolor=COLORS["accent"],
        )
        self.password_entry.pack(fill="x", pady=(0, 20))

        tk.Button(
            card, text="Войти",
            font=(FONT, 14, "bold"), bg=COLORS["accent"], fg=COLORS["bg"],
            relief="flat", bd=0, padx=30, pady=14, cursor="hand2",
            command=self._authenticate,
        ).pack(fill="x", padx=52)

        self.root.bind("<Return>", lambda _e: self._authenticate())

        # Подсказка по логинам (можно убрать в production)
        hint = (
            "Логин: student_demo / stud2026  |  teacher_demo / teach2026\n"
            "admin_demo / admin2026  |  accountant_demo / acc2026"
        )
        tk.Label(self.root, text=hint, font=(FONT, 9), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(side="bottom", pady=10)

    def _authenticate(self) -> None:
        login    = self.login_entry.get().strip() if self.login_entry else ""
        password = self.password_entry.get().strip() if self.password_entry else ""
        user     = self.auth_service.authenticate_password(login, password)
        if user is None:
            messagebox.showerror("Вход", "Неверный логин или пароль, либо учётная запись заблокирована.")
            return
        self.root.destroy()
        self.on_login_success(user)


class MainApp:
    def __init__(self, current_user: SessionUser) -> None:
        self.root = tk.Tk()
        self.current_user = current_user
        self.rbac = RBACService()
        self.output_area: tk.Frame | None = None

        self.schedule_module: ScheduleModule | None = None
        self.grades_module:   GradesModule   | None = None
        self.students_module: StudentsModule  | None = None
        self.teachers_module: TeachersModule  | None = None
        self.users_module:    UsersModule     | None = None
        self.finance_module:  FinanceModule   | None = None

        self.root.title(WINDOW_TITLE)
        self.root.state("zoomed")
        self.root.geometry("1440x860")
        self.root.minsize(1200, 720)
        self.root.configure(bg=COLORS["bg"])
        self._create_widgets()

    def _create_widgets(self) -> None:
        # ── Верхняя панель ──
        top = tk.Frame(self.root, bg=COLORS["frame"], height=56)
        top.pack(fill="x")
        top.pack_propagate(False)

        role_label = self.rbac.role_title(self.current_user.role)
        tk.Label(
            top,
            text=f"{self.current_user.full_name}   •   {role_label}",
            font=(FONT, 12),
            bg=COLORS["frame"], fg=COLORS["text"],
        ).pack(side="left", padx=22)
        tk.Button(
            top, text="Выйти",
            font=(FONT, 11, "bold"), bg=COLORS["error"], fg=COLORS["bg"],
            relief="flat", padx=18, pady=8, cursor="hand2",
            command=self._logout,
        ).pack(side="right", padx=22)

        # ── Основной layout ──
        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=18, pady=16)

        sidebar = tk.Frame(body, bg=COLORS["frame"], width=260)
        sidebar.pack(side="left", fill="y", padx=(0, 16))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="НАВИГАЦИЯ",
            font=(FONT, 11, "bold"), bg=COLORS["frame"], fg=COLORS["accent"],
        ).pack(pady=(22, 14))

        self._active_btn: tk.Button | None = None

        for item in self.rbac.allowed_menu(self.current_user.role):
            btn = tk.Button(
                sidebar,
                text=item["title"],
                font=(FONT, 11),
                bg=COLORS["button"], fg=COLORS["text"],
                relief="flat", padx=12, pady=11,
                activebackground=COLORS["button_hover"],
                cursor="hand2",
                anchor="w",
                command=lambda r=item["resource"]: self._open_section(r),
            )
            btn.pack(fill="x", padx=14, pady=4)

        self.output_area = tk.Frame(body, bg=COLORS["frame"])
        self.output_area.pack(side="right", fill="both", expand=True)

        self.schedule_module = ScheduleModule(self.output_area, self.current_user)
        self.grades_module   = GradesModule(self.output_area, self.current_user, self.rbac)
        self.students_module = StudentsModule(self.output_area, self.current_user)
        self.teachers_module = TeachersModule(self.output_area)
        self.users_module    = UsersModule(self.output_area)
        self.finance_module  = FinanceModule(self.output_area, self.current_user)

        self._show_welcome()

    def _show_welcome(self) -> None:
        self._clear_output()
        tk.Label(
            self.output_area,
            text=f"Добро пожаловать, {self.current_user.full_name}!",
            font=(FONT, 20, "bold"),
            bg=COLORS["frame"], fg=COLORS["accent"],
        ).pack(pady=(48, 18))

        if self.current_user.role == "student" and self.current_user.student_id is not None:
            from data_sample import STUDENTS
            student = next((s for s in STUDENTS if s["id"] == self.current_user.student_id), None)
            if student:
                card = tk.Frame(self.output_area, bg=COLORS["bg"],
                                highlightthickness=1, highlightbackground=COLORS["line"])
                card.pack(padx=26, pady=10, fill="x")
                for title, value in [
                    ("Группа",           student["group"]),
                    ("Зачётная книжка",  student["record_book"]),
                    ("Курс",             f"{student['course']} курс"),
                    ("Форма обучения",   student["study_form"]),
                    ("Основа",           student["funding"]),
                    ("Статус",           student["status"]),
                ]:
                    line = tk.Frame(card, bg=COLORS["bg"])
                    line.pack(fill="x", padx=22, pady=10)
                    tk.Label(line, text=title, width=20, anchor="w",
                             font=(FONT, 12, "bold"), bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
                    tk.Label(line, text=value, anchor="w",
                             font=(FONT, 12), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(side="left")
            return

        tk.Label(
            self.output_area,
            text=self.rbac.role_title(self.current_user.role),
            font=(FONT, 13), bg=COLORS["frame"], fg=COLORS["subtext"],
        ).pack()

    def _open_section(self, resource: str) -> None:
        mapping = {
            "schedule": self.schedule_module,
            "grades":   self.grades_module,
            "students": self.students_module,
            "teachers": self.teachers_module,
            "users":    self.users_module,
            "finance":  self.finance_module,
        }
        module = mapping.get(resource)
        if module:
            module.render()

    def _clear_output(self) -> None:
        assert self.output_area is not None
        for w in self.output_area.winfo_children():
            w.destroy()

    def _logout(self) -> None:
        if messagebox.askyesno("Выход", "Завершить текущий сеанс?"):
            self.root.destroy()
            root = tk.Tk()
            LoginWindow(root, _start_main_app)
            root.mainloop()

    def run(self) -> None:
        self.root.mainloop()


def _start_main_app(user: SessionUser) -> None:
    MainApp(user).run()


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, _start_main_app)
    root.mainloop()

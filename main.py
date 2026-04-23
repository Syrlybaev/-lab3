from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

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
        self.root.title(f"{WINDOW_TITLE} - Вход")
        self.root.geometry("720x560")
        self.root.minsize(640, 500)
        self.root.configure(bg=COLORS["bg"])
        self.create_widgets()

    def create_widgets(self) -> None:
        card = tk.Frame(self.root, bg=COLORS["frame"], bd=0, highlightthickness=1, highlightbackground=COLORS["line"])
        card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=360)

        tk.Label(
            card,
            text="ВИРТУАЛЬНЫЙ ДЕКАНАТ",
            font=(FONT, 22, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(28, 18))

        form = tk.Frame(card, bg=COLORS["frame"])
        form.pack(fill="x", padx=52)

        tk.Label(form, text="Логин", font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 5))
        self.login_entry = tk.Entry(
            form,
            font=(FONT, 13),
            bg=COLORS["bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
        )
        self.login_entry.pack(fill="x", pady=(0, 18))

        tk.Label(form, text="Пароль", font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 5))
        self.password_entry = tk.Entry(
            form,
            font=(FONT, 13),
            show="*",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
        )
        self.password_entry.pack(fill="x", pady=(0, 18))

        tk.Button(
            card,
            text="Войти",
            font=(FONT, 14, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["bg"],
            relief="flat",
            bd=0,
            padx=30,
            pady=14,
            cursor="hand2",
            command=self.authenticate,
        ).pack(fill="x", padx=52, pady=(24, 0))

        self.root.bind("<Return>", lambda _event: self.authenticate())

    def authenticate(self) -> None:
        login = self.login_entry.get().strip() if self.login_entry else ""
        password = self.password_entry.get().strip() if self.password_entry else ""
        user = self.auth_service.authenticate_password(login, password)
        if user is None:
            messagebox.showerror("Вход", "Неверный логин, пароль или учетная запись заблокирована.")
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
        self.grades_module: GradesModule | None = None
        self.students_module: StudentsModule | None = None
        self.teachers_module: TeachersModule | None = None
        self.users_module: UsersModule | None = None

        self.root.title(WINDOW_TITLE)
        self.root.state("zoomed")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 720)
        self.root.configure(bg=COLORS["bg"])
        self.create_widgets()

    def create_widgets(self) -> None:
        top_frame = tk.Frame(self.root, bg=COLORS["frame"], height=58)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)

        user_text = self.current_user.full_name
        tk.Label(
            top_frame,
            text=user_text,
            font=(FONT, 12),
            bg=COLORS["frame"],
            fg=COLORS["text"],
        ).pack(side="left", padx=22)
        tk.Button(
            top_frame,
            text="Выйти",
            font=(FONT, 11, "bold"),
            bg=COLORS["error"],
            fg=COLORS["bg"],
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.logout,
        ).pack(side="right", padx=22)

        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=18)

        sidebar = tk.Frame(body, bg=COLORS["frame"], width=300)
        sidebar.pack(side="left", fill="y", padx=(0, 18))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="ДОСТУПНЫЕ РАЗДЕЛЫ",
            font=(FONT, 12, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(24, 18))

        for item in self.rbac.allowed_menu(self.current_user.role):
            tk.Button(
                sidebar,
                text=item["title"],
                font=(FONT, 11),
                bg=COLORS["button"],
                fg=COLORS["text"],
                relief="flat",
                padx=12,
                pady=10,
                activebackground=COLORS["button_hover"],
                cursor="hand2",
                command=lambda resource=item["resource"]: self.open_section(resource),
            ).pack(fill="x", padx=16, pady=5)

        self.output_area = tk.Frame(body, bg=COLORS["frame"])
        self.output_area.pack(side="right", fill="both", expand=True)

        self.schedule_module = ScheduleModule(self.output_area, self.current_user)
        self.grades_module = GradesModule(self.output_area, self.current_user, self.rbac)
        self.students_module = StudentsModule(self.output_area, self.current_user)
        self.teachers_module = TeachersModule(self.output_area)
        self.users_module = UsersModule(self.output_area)
        self.show_welcome()

    def show_welcome(self) -> None:
        self.clear_output()
        tk.Label(
            self.output_area,
            text=f"Здравствуйте, {self.current_user.full_name}",
            font=(FONT, 22, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(48, 18))

        if self.current_user.role == "student" and self.current_user.student_id is not None:
            from data_sample import STUDENTS

            student = next(item for item in STUDENTS if item["id"] == self.current_user.student_id)
            card = tk.Frame(self.output_area, bg=COLORS["bg"], highlightthickness=1, highlightbackground=COLORS["line"])
            card.pack(padx=26, pady=10, fill="x")
            rows = [
                ("Группа", student["group"]),
                ("Зачетная книжка", student["record_book"]),
                ("Курс", f"{student['course']} курс"),
            ]
            for title, value in rows:
                line = tk.Frame(card, bg=COLORS["bg"])
                line.pack(fill="x", padx=20, pady=12)
                tk.Label(line, text=title, width=18, anchor="w", font=(FONT, 12, "bold"), bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
                tk.Label(line, text=value, anchor="w", font=(FONT, 12), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(side="left")
            return

        tk.Label(
            self.output_area,
            text=self.rbac.role_title(self.current_user.role),
            font=(FONT, 13),
            bg=COLORS["frame"],
            fg=COLORS["subtext"],
        ).pack()

    def open_section(self, resource: str) -> None:
        if resource == "schedule":
            self.schedule_module.render()
        elif resource == "grades":
            self.grades_module.render()
        elif resource == "students":
            self.students_module.render()
        elif resource == "teachers":
            self.teachers_module.render()
        elif resource == "users":
            self.users_module.render()

    def clear_output(self) -> None:
        assert self.output_area is not None
        for widget in self.output_area.winfo_children():
            widget.destroy()

    def logout(self) -> None:
        if messagebox.askyesno("Выход", "Завершить текущий сеанс?"):
            self.root.destroy()
            root = tk.Tk()
            LoginWindow(root, start_main_app)
            root.mainloop()

    def run(self) -> None:
        self.root.mainloop()


def start_main_app(user: SessionUser) -> None:
    app = MainApp(user)
    app.run()


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, start_main_app)
    root.mainloop()

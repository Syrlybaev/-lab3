from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from data_sample import (
    DEGREES,
    DEPARTMENTS,
    INSTITUTES,
    POSITIONS,
    SUBJECTS,
    TEACHERS,
    TEACHER_DEPARTMENTS,
    TEACHER_POSITIONS,
    TEACHER_SUBJECTS,
)
from services.auth import SessionUser
from services.rbac import RBACService
from ui.theme import COLORS, FONT


class TeachersModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser, rbac: RBACService) -> None:
        self.host_frame = host_frame
        self.current_user = current_user
        self.rbac = rbac
        self.tree: ttk.Treeview | None = None
        self.details_frame: tk.Frame | None = None

    def render(self) -> None:
        self._clear()
        self._header()
        main = tk.Frame(self.host_frame, bg=COLORS["frame"])
        main.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = tk.Frame(main, bg=COLORS["frame"], width=560)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(main, bg=COLORS["bg"], width=380)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)
        self.details_frame = right

        self._toolbar(left)
        self._teachers_table(left)
        self._render_permission_hint(right)

    def _header(self) -> None:
        tk.Label(self.host_frame, text="МОДУЛЬ " + "ПРЕПОДАВАТЕЛИ", font=(FONT, 18, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(12, 8))
        tk.Label(
            self.host_frame,
            text="Институты, кафедры, должности, учёные степени, преподаватели, дисциплины и назначения.",
            font=(FONT, 11),
            bg=COLORS["frame"],
            fg=COLORS["subtext"],
        ).pack(pady=(0, 8))

    def _toolbar(self, parent: tk.Frame) -> None:
        bar = tk.Frame(parent, bg=COLORS["frame"])
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="Список преподавателей", font=(FONT, 12, "bold"), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left")
        if self.rbac.check(self.current_user.roles, "teachers", "create_teacher").allowed:
            tk.Button(bar, text="Добавить", font=(FONT, 10, "bold"), bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=12, pady=6, cursor="hand2", command=self._add_teacher_dialog).pack(side="right", padx=(8, 0))
        if self.rbac.check(self.current_user.roles, "teachers", "assign_subject").allowed:
            tk.Button(bar, text="Назначить дисциплину", font=(FONT, 10), bg=COLORS["button"], fg=COLORS["text"], relief="flat", padx=12, pady=6, cursor="hand2", command=self._assign_subject_dialog).pack(side="right")

    def _teachers_table(self, parent: tk.Frame) -> None:
        columns = ("fio", "departments", "positions", "degree", "email")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Teachers.Treeview", background=COLORS["bg"], foreground=COLORS["text"], fieldbackground=COLORS["bg"], font=(FONT, 10))
        style.configure("Teachers.Treeview.Heading", background=COLORS["button"], foreground=COLORS["text"], font=(FONT, 10, "bold"))
        tree.configure(style="Teachers.Treeview")
        headings = {
            "fio": "ФИО",
            "departments": "Кафедры",
            "positions": "Должности",
            "degree": "Степень",
            "email": "Email",
        }
        for key, title in headings.items():
            tree.heading(key, text=title)
        tree.column("fio", width=180, anchor="w")
        tree.column("departments", width=220, anchor="w")
        tree.column("positions", width=170, anchor="w")
        tree.column("degree", width=100, anchor="center")
        tree.column("email", width=170, anchor="w")

        for teacher in self._visible_teachers():
            tree.insert("", "end", iid=str(teacher["id"]), values=(
                self._teacher_fio(teacher),
                ", ".join(self._department_names(teacher["id"])),
                ", ".join(self._position_names(teacher["id"])),
                self._degree_name(teacher["degree_id"]),
                teacher["email"],
            ))
        tree.bind("<<TreeviewSelect>>", self._on_select_teacher)
        tree.pack(fill="both", expand=True)
        self.tree = tree

    def _render_permission_hint(self, parent: tk.Frame) -> None:
        for widget in parent.winfo_children():
            widget.destroy()
        box = tk.Frame(parent, bg=COLORS["bg"])
        box.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(box, text="Информация и действия", font=(FONT, 12, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        explanation = self.rbac.explain_permissions(self.current_user.roles)
        info_lines = [
            f"Пользователь: {self.current_user.full_name}",
            f"Роли: {self.rbac.role_titles(self.current_user.roles)}",
            "",
            "Доступные права в преподавательском модуле:",
        ]
        for action in explanation.get("teachers", []):
            info_lines.append(f"• {self._action_title(action)}")
        tk.Label(box, text="\n".join(info_lines), justify="left", font=(FONT, 10), bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")

    def _on_select_teacher(self, _event: object) -> None:
        if not self.tree or not self.details_frame:
            return
        selected = self.tree.selection()
        if not selected:
            return
        teacher_id = int(selected[0])
        teacher = next(t for t in TEACHERS if t["id"] == teacher_id)
        self._show_teacher_card(teacher)

    def _show_teacher_card(self, teacher: dict) -> None:
        assert self.details_frame is not None
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        card = tk.Frame(self.details_frame, bg=COLORS["bg"])
        card.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(card, text=self._teacher_fio(teacher), font=(FONT, 14, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w")
        rows = [
            ("Email", teacher["email"]),
            ("Телефон", teacher["phone"]),
            ("Учёная степень", self._degree_name(teacher["degree_id"])),
            ("Кафедры", ", ".join(self._department_names(teacher["id"]))),
            ("Должности", ", ".join(self._position_names(teacher["id"]))),
            ("Дисциплины", "\n".join(self._subject_lines(teacher["id"])) or "Нет назначений"),
        ]
        for label, value in rows:
            tk.Label(card, text=f"{label}:", font=(FONT, 10, "bold"), bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(10 if label == "Email" else 6, 0))
            tk.Label(card, text=value, justify="left", font=(FONT, 10), bg=COLORS["bg"], fg=COLORS["subtext"], wraplength=320).pack(anchor="w")
        btn_bar = tk.Frame(card, bg=COLORS["bg"])
        btn_bar.pack(anchor="w", pady=14)
        if self.rbac.check(self.current_user.roles, "teachers", "edit_teacher").allowed:
            tk.Button(btn_bar, text="Редактировать email", bg=COLORS["button"], fg=COLORS["text"], relief="flat", padx=10, pady=6, cursor="hand2", command=lambda: self._edit_email_dialog(teacher)).pack(side="left", padx=(0, 8))
        if self.rbac.check(self.current_user.roles, "teachers", "assign_department").allowed:
            tk.Button(btn_bar, text="Добавить кафедру", bg=COLORS["button"], fg=COLORS["text"], relief="flat", padx=10, pady=6, cursor="hand2", command=lambda: self._assign_department_dialog(teacher)).pack(side="left")

    def _visible_teachers(self) -> list[dict]:
        can_view_all = self.rbac.check(self.current_user.roles, "teachers", "view_all").allowed
        can_view_self = self.rbac.check(self.current_user.roles, "teachers", "view_self").allowed
        if can_view_all:
            if "head_of_department" in self.current_user.roles and "dean_admin" not in self.current_user.roles:
                result = []
                allowed = set(self.current_user.departments)
                for teacher in TEACHERS:
                    if allowed & set(self._department_ids(teacher["id"])):
                        result.append(teacher)
                return result
            return list(TEACHERS)
        if can_view_self and self.current_user.teacher_id is not None:
            return [teacher for teacher in TEACHERS if teacher["id"] == self.current_user.teacher_id]
        return []

    def _teacher_fio(self, teacher: dict) -> str:
        return f"{teacher['last_name']} {teacher['first_name']} {teacher['patronymic']}"

    def _department_ids(self, teacher_id: int) -> list[int]:
        return [item["department_id"] for item in TEACHER_DEPARTMENTS if item["teacher_id"] == teacher_id]

    def _department_names(self, teacher_id: int) -> list[str]:
        dep_ids = set(self._department_ids(teacher_id))
        return [dep["name"] for dep in DEPARTMENTS if dep["id"] in dep_ids]

    def _position_names(self, teacher_id: int) -> list[str]:
        pos_ids = {item["position_id"] for item in TEACHER_POSITIONS if item["teacher_id"] == teacher_id}
        return [pos["name"] for pos in POSITIONS if pos["id"] in pos_ids]

    def _degree_name(self, degree_id: int) -> str:
        return next((degree["name"] for degree in DEGREES if degree["id"] == degree_id), "—")

    def _subject_lines(self, teacher_id: int) -> list[str]:
        lines = []
        for link in TEACHER_SUBJECTS:
            if link["teacher_id"] != teacher_id:
                continue
            subject = next(sub for sub in SUBJECTS if sub["id"] == link["subject_id"])
            dep = next(dep for dep in DEPARTMENTS if dep["id"] == subject["department_id"])
            lines.append(f"{subject['name']} [{link['semester']}] — {link['description']} ({dep['name']})")
        return lines

    def _action_title(self, action: str) -> str:
        titles = {
            "view_all": "просмотр списка преподавателей",
            "view_self": "просмотр собственной карточки преподавателя",
            "create_teacher": "создание преподавателя",
            "edit_teacher": "редактирование преподавателя",
            "assign_department": "привязка кафедры",
            "assign_position": "привязка должности",
            "assign_subject": "назначение дисциплины",
        }
        return titles.get(action, action)

    def _add_teacher_dialog(self) -> None:
        dialog = tk.Toplevel(self.host_frame)
        dialog.title("Добавить преподавателя")
        dialog.configure(bg=COLORS["frame"])
        dialog.resizable(False, False)
        fields = {}
        labels = [
            ("last_name", "Фамилия"),
            ("first_name", "Имя"),
            ("patronymic", "Отчество"),
            ("email", "Email"),
            ("phone", "Телефон"),
        ]
        for idx, (key, title) in enumerate(labels):
            tk.Label(dialog, text=title, bg=COLORS["frame"], fg=COLORS["text"], font=(FONT, 10)).grid(row=idx, column=0, sticky="w", padx=12, pady=6)
            entry = tk.Entry(dialog, width=36)
            entry.grid(row=idx, column=1, padx=12, pady=6)
            fields[key] = entry
        tk.Label(dialog, text="Степень", bg=COLORS["frame"], fg=COLORS["text"], font=(FONT, 10)).grid(row=len(labels), column=0, sticky="w", padx=12, pady=6)
        degree_var = tk.StringVar(value=DEGREES[0]["name"])
        ttk.Combobox(dialog, textvariable=degree_var, state="readonly", values=[d["name"] for d in DEGREES], width=33).grid(row=len(labels), column=1, padx=12, pady=6)

        def save() -> None:
            if not fields["last_name"].get().strip() or not fields["first_name"].get().strip():
                messagebox.showerror("Ошибка", "Фамилия и имя обязательны")
                return
            new_id = max(t["id"] for t in TEACHERS) + 1
            degree_id = next(d["id"] for d in DEGREES if d["name"] == degree_var.get())
            TEACHERS.append({
                "id": new_id,
                "last_name": fields["last_name"].get().strip(),
                "first_name": fields["first_name"].get().strip(),
                "patronymic": fields["patronymic"].get().strip(),
                "email": fields["email"].get().strip() or f"teacher{new_id}@vdekanat.local",
                "phone": fields["phone"].get().strip() or "79000000000",
                "degree_id": degree_id,
            })
            messagebox.showinfo("Успешно", "Преподаватель добавлен")
            dialog.destroy()
            self.render()

        tk.Button(dialog, text="Сохранить", command=save, bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=12, pady=6).grid(row=len(labels) + 1, column=0, columnspan=2, pady=12)

    def _assign_department_dialog(self, teacher: dict) -> None:
        dialog = tk.Toplevel(self.host_frame)
        dialog.title("Добавить кафедру преподавателю")
        dialog.configure(bg=COLORS["frame"])
        tk.Label(dialog, text=self._teacher_fio(teacher), bg=COLORS["frame"], fg=COLORS["accent"], font=(FONT, 11, "bold")).pack(padx=12, pady=(12, 8))
        dep_var = tk.StringVar(value=DEPARTMENTS[0]["name"])
        ttk.Combobox(dialog, textvariable=dep_var, state="readonly", values=[d["name"] for d in DEPARTMENTS], width=42).pack(padx=12, pady=8)

        def save() -> None:
            dep = next(d for d in DEPARTMENTS if d["name"] == dep_var.get())
            if any(item for item in TEACHER_DEPARTMENTS if item["teacher_id"] == teacher["id"] and item["department_id"] == dep["id"]):
                messagebox.showwarning("Внимание", "Эта кафедра уже назначена")
                return
            if "head_of_department" in self.current_user.roles and "dean_admin" not in self.current_user.roles and dep["id"] not in self.current_user.departments:
                messagebox.showerror("Ошибка", "Заведующий кафедрой может назначать только свою кафедру")
                return
            TEACHER_DEPARTMENTS.append({"teacher_id": teacher["id"], "department_id": dep["id"]})
            messagebox.showinfo("Успешно", "Кафедра добавлена")
            dialog.destroy()
            self.render()

        tk.Button(dialog, text="Назначить", command=save, bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=12, pady=6).pack(pady=(4, 12))

    def _assign_subject_dialog(self) -> None:
        visible_teachers = self._visible_teachers()
        if not visible_teachers:
            messagebox.showerror("Ошибка", "Нет доступных преподавателей для назначения")
            return
        dialog = tk.Toplevel(self.host_frame)
        dialog.title("Назначить дисциплину")
        dialog.configure(bg=COLORS["frame"])
        teacher_var = tk.StringVar(value=self._teacher_fio(visible_teachers[0]))
        subject_var = tk.StringVar(value=SUBJECTS[0]["name"])
        semester_var = tk.StringVar(value="2026-1")
        desc_var = tk.StringVar(value="Лекции")
        rows = [
            ("Преподаватель", teacher_var, [self._teacher_fio(t) for t in visible_teachers]),
            ("Дисциплина", subject_var, [s["name"] for s in SUBJECTS]),
            ("Семестр", semester_var, ["2025-2", "2026-1", "2026-2"]),
            ("Тип ведения", desc_var, ["Лекции", "Практика", "Лабораторные", "Лекции и лабораторные"]),
        ]
        for idx, (title, variable, values) in enumerate(rows):
            tk.Label(dialog, text=title, bg=COLORS["frame"], fg=COLORS["text"], font=(FONT, 10)).grid(row=idx, column=0, sticky="w", padx=12, pady=6)
            ttk.Combobox(dialog, textvariable=variable, state="readonly", values=values, width=34).grid(row=idx, column=1, padx=12, pady=6)

        def save() -> None:
            teacher = next(t for t in visible_teachers if self._teacher_fio(t) == teacher_var.get())
            subject = next(s for s in SUBJECTS if s["name"] == subject_var.get())
            if "head_of_department" in self.current_user.roles and "dean_admin" not in self.current_user.roles:
                if subject["department_id"] not in self.current_user.departments:
                    messagebox.showerror("Ошибка", "Заведующий кафедрой может назначать дисциплины только своей кафедры")
                    return
            new_id = max((item["id"] for item in TEACHER_SUBJECTS), default=0) + 1
            TEACHER_SUBJECTS.append({"id": new_id, "teacher_id": teacher["id"], "subject_id": subject["id"], "semester": semester_var.get(), "description": desc_var.get()})
            messagebox.showinfo("Успешно", "Дисциплина назначена")
            dialog.destroy()
            self.render()

        tk.Button(dialog, text="Сохранить", command=save, bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=12, pady=6).grid(row=len(rows), column=0, columnspan=2, pady=12)

    def _edit_email_dialog(self, teacher: dict) -> None:
        dialog = tk.Toplevel(self.host_frame)
        dialog.title("Изменить email")
        dialog.configure(bg=COLORS["frame"])
        tk.Label(dialog, text=self._teacher_fio(teacher), bg=COLORS["frame"], fg=COLORS["accent"], font=(FONT, 11, "bold")).pack(padx=12, pady=(12, 8))
        entry = tk.Entry(dialog, width=42)
        entry.insert(0, teacher["email"])
        entry.pack(padx=12, pady=8)

        def save() -> None:
            teacher["email"] = entry.get().strip() or teacher["email"]
            messagebox.showinfo("Успешно", "Email обновлён")
            dialog.destroy()
            self.render()

        tk.Button(dialog, text="Сохранить", command=save, bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=12, pady=6).pack(pady=(4, 12))

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

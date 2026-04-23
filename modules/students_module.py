from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from data_sample import GRADE_RECORDS, SCHEDULE_DATA, STUDENTS
from services.auth import SessionUser
from ui.theme import COLORS, FONT


class StudentsModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser) -> None:
        self.host_frame = host_frame
        self.current_user = current_user
        self.tree: ttk.Treeview | None = None
        self.details_frame: tk.Frame | None = None

    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="СТУДЕНТЫ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 6))
        tk.Label(
            self.host_frame,
            text=self._intro_text(),
            font=(FONT, 11),
            bg=COLORS["frame"],
            fg=COLORS["subtext"],
        ).pack(pady=(0, 10))

        content = tk.Frame(self.host_frame, bg=COLORS["frame"])
        content.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = tk.Frame(content, bg=COLORS["frame"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(content, bg=COLORS["bg"], width=330)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self.details_frame = right

        columns = ("full_name", "group", "record_book", "funding", "status")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        headings = {
            "full_name": "ФИО",
            "group": "Группа",
            "record_book": "Зачетная книжка",
            "funding": "Основа",
            "status": "Статус",
        }
        widths = {
            "full_name": 220,
            "group": 100,
            "record_book": 130,
            "funding": 100,
            "status": 140,
        }
        for key, title in headings.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="w")

        for student in self._visible_students():
            tree.insert(
                "",
                "end",
                iid=str(student["id"]),
                values=(
                    student["full_name"],
                    student["group"],
                    student["record_book"],
                    student["funding"],
                    student["status"],
                ),
            )
        tree.bind("<<TreeviewSelect>>", self._on_select)
        tree.pack(fill="both", expand=True)
        self.tree = tree

        self._render_details(None)

    def _visible_students(self) -> list[dict]:
        students = list(STUDENTS)
        if self.current_user.role == "teacher" and self.current_user.teacher_id is not None:
            groups = {
                item["group"]
                for item in SCHEDULE_DATA
                if item["teacher_id"] == self.current_user.teacher_id
            }
            students = [student for student in students if student["group"] in groups]
        return sorted(students, key=lambda item: (item["group"], item["full_name"]))

    def _intro_text(self) -> str:
        if self.current_user.role == "teacher":
            return "Показаны студенты только тех групп, где ведет занятия текущий преподаватель."
        return "Полный реестр студентов виртуального деканата."

    def _on_select(self, _event: object) -> None:
        if not self.tree:
            return
        selected = self.tree.selection()
        if not selected:
            self._render_details(None)
            return
        student = next(item for item in STUDENTS if item["id"] == int(selected[0]))
        self._render_details(student)

    def _render_details(self, student: dict | None) -> None:
        assert self.details_frame is not None
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        box = tk.Frame(self.details_frame, bg=COLORS["bg"])
        box.pack(fill="both", expand=True, padx=12, pady=12)

        if student is None:
            tk.Label(
                box,
                text="Выберите студента, чтобы посмотреть карточку.",
                justify="left",
                wraplength=280,
                font=(FONT, 10),
                bg=COLORS["bg"],
                fg=COLORS["subtext"],
            ).pack(anchor="w")
            return

        tk.Label(
            box,
            text=student["full_name"],
            font=(FONT, 13, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["accent"],
            wraplength=280,
            justify="left",
        ).pack(anchor="w")

        average = self._student_average(student["id"])
        info_lines = [
            f"Группа: {student['group']}",
            f"Зачетная книжка: {student['record_book']}",
            f"Направление: {student['program']}",
            f"Форма обучения: {student['study_form']}",
            f"Основа: {student['funding']}",
            f"Статус: {student['status']}",
            f"Средний рейтинг: {average:.1f}",
        ]
        tk.Label(
            box,
            text="\n".join(info_lines),
            justify="left",
            wraplength=280,
            font=(FONT, 10),
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(10, 0))

    def _student_average(self, student_id: int) -> float:
        grades = [item["points"] for item in GRADE_RECORDS if item["student_id"] == student_id]
        if not grades:
            return 0.0
        return sum(grades) / len(grades)

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from data_sample import GRADE_AUDIT, GRADE_RECORDS, STUDENTS, TEACHERS
from services.auth import SessionUser
from services.rbac import RBACService
from ui.theme import COLORS, FONT


class GradesModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser, rbac: RBACService) -> None:
        self.host_frame = host_frame
        self.current_user = current_user
        self.rbac = rbac
        self.tree: ttk.Treeview | None = None

    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="МОДУЛЬНЫЙ ЖУРНАЛ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 6))

        toolbar = tk.Frame(self.host_frame, bg=COLORS["frame"])
        toolbar.pack(fill="x", pady=(0, 8))
        if self.rbac.check(self.current_user.role, "grades", "edit").allowed:
            tk.Button(
                toolbar,
                text="Изменить оценку",
                font=(FONT, 10, "bold"),
                bg=COLORS["accent"],
                fg=COLORS["bg"],
                relief="flat",
                padx=12,
                pady=6,
                cursor="hand2",
                command=self._edit_selected_grade,
            ).pack(side="right", padx=12)

        if self.current_user.role == "student":
            columns = ("subject", "m1", "m2", "credit", "exam", "coefficient")
            headings = {
                "subject": "ПРЕДМЕТ",
                "m1": "М1",
                "m2": "М2",
                "credit": "З",
                "exam": "Э",
                "coefficient": "К",
            }
            widths = {
                "subject": 320,
                "m1": 80,
                "m2": 80,
                "credit": 80,
                "exam": 80,
                "coefficient": 80,
            }
        else:
            columns = ("student", "group", "subject", "m1", "m2", "credit", "exam", "coefficient", "teacher")
            headings = {
                "student": "Студент",
                "group": "Группа",
                "subject": "Дисциплина",
                "m1": "М1",
                "m2": "М2",
                "credit": "З",
                "exam": "Э",
                "coefficient": "К",
                "teacher": "Преподаватель",
            }
            widths = {
                "student": 185,
                "group": 90,
                "subject": 210,
                "m1": 65,
                "m2": 65,
                "credit": 65,
                "exam": 65,
                "coefficient": 65,
                "teacher": 180,
            }

        tree = ttk.Treeview(self.host_frame, columns=columns, show="headings", height=18)
        for key, title in headings.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="center" if key in {"m1", "m2", "credit", "exam", "coefficient"} else "w")

        for grade in self._visible_grades():
            values = (
                grade["subject"],
                grade["m1"],
                grade["m2"],
                self._credit_value(grade),
                self._exam_value(grade),
                f"{grade['coefficient']:.1f}",
            )
            if self.current_user.role != "student":
                values = (
                    self._student_name(grade["student_id"]),
                    grade["group"],
                    *values,
                    self._teacher_name(grade["teacher_id"]),
                )
            tree.insert("", "end", iid=str(grade["id"]), values=values)
        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.tree = tree

        tk.Label(
            self.host_frame,
            text=f"Средний результат по видимым записям: {self._average_points():.1f}",
            font=(FONT, 11, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["success"],
        ).pack(anchor="w", padx=12, pady=(0, 10))

    def _visible_grades(self) -> list[dict]:
        records = list(GRADE_RECORDS)
        if self.current_user.role == "student" and self.current_user.student_id is not None:
            records = [item for item in records if item["student_id"] == self.current_user.student_id]
        elif self.current_user.role == "teacher" and self.current_user.teacher_id is not None:
            records = [item for item in records if item["teacher_id"] == self.current_user.teacher_id]
        return sorted(records, key=lambda item: (item["group"], item["student_id"], item["subject"]))

    def _average_points(self) -> float:
        visible = self._visible_grades()
        if not visible:
            return 0.0
        return sum(item["points"] for item in visible) / len(visible)

    def _student_name(self, student_id: int) -> str:
        return next(student["full_name"] for student in STUDENTS if student["id"] == student_id)

    def _teacher_name(self, teacher_id: int) -> str:
        return next(teacher["full_name"] for teacher in TEACHERS if teacher["id"] == teacher_id)

    def _credit_value(self, grade: dict) -> str:
        if grade["control_type"] == "Зачет":
            return str(grade["points"])
        return "-"

    def _exam_value(self, grade: dict) -> str:
        if grade["control_type"] == "Экзамен":
            return str(grade["points"])
        return "-"

    def _edit_selected_grade(self) -> None:
        if not self.tree:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Оценки", "Сначала выберите запись журнала.")
            return

        grade = next(item for item in GRADE_RECORDS if item["id"] == int(selected[0]))
        dialog = tk.Toplevel(self.host_frame)
        dialog.title("Изменение оценки")
        dialog.configure(bg=COLORS["frame"])
        dialog.resizable(False, False)

        points_var = tk.StringVar(value=str(grade["points"]))
        status_var = tk.StringVar(value=grade["status"])
        comment_var = tk.StringVar(value="Корректировка по итогам проверки")

        fields = [
            ("Студент", self._student_name(grade["student_id"]), None),
            ("Дисциплина", grade["subject"], None),
            ("Баллы", points_var, "entry"),
            ("Статус", status_var, "combo"),
            ("Комментарий", comment_var, "entry"),
        ]

        for row, (title, value, field_type) in enumerate(fields):
            tk.Label(dialog, text=title, bg=COLORS["frame"], fg=COLORS["text"], font=(FONT, 10)).grid(row=row, column=0, sticky="w", padx=12, pady=6)
            if field_type is None:
                tk.Label(dialog, text=value, bg=COLORS["frame"], fg=COLORS["subtext"], font=(FONT, 10)).grid(row=row, column=1, sticky="w", padx=12, pady=6)
            elif field_type == "entry":
                tk.Entry(dialog, textvariable=value, width=34).grid(row=row, column=1, padx=12, pady=6)
            else:
                ttk.Combobox(dialog, textvariable=value, state="readonly", values=["Подтверждена", "Пересдача", "Неявка"], width=31).grid(row=row, column=1, padx=12, pady=6)

        def save() -> None:
            try:
                new_points = int(points_var.get().strip())
            except ValueError:
                messagebox.showerror("Оценки", "Баллы должны быть целым числом.")
                return
            if not 0 <= new_points <= 54:
                messagebox.showerror("Оценки", "Баллы должны быть в диапазоне от 0 до 54.")
                return
            old_points = grade["points"]
            grade["points"] = new_points
            grade["status"] = status_var.get().strip() or grade["status"]
            GRADE_AUDIT.append(
                {
                    "grade_id": grade["id"],
                    "changed_by": self.current_user.login,
                    "old_value": old_points,
                    "new_value": new_points,
                    "changed_at": "2026-04-23 12:00",
                    "comment": comment_var.get().strip() or "Без комментария",
                }
            )
            dialog.destroy()
            self.render()

        tk.Button(
            dialog,
            text="Сохранить",
            command=save,
            bg=COLORS["accent"],
            fg=COLORS["bg"],
            relief="flat",
            padx=12,
            pady=6,
        ).grid(row=len(fields), column=0, columnspan=2, pady=12)

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from data_sample import DAY_ORDER, SCHEDULE_DATA, STUDENTS, TEACHERS
from services.auth import SessionUser
from ui.theme import COLORS, FONT


class ScheduleModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser) -> None:
        self.host_frame = host_frame
        self.current_user = current_user

    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="РАСПИСАНИЕ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 6))
        notebook = ttk.Notebook(self.host_frame)
        notebook.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        columns = ("pair", "time", "subject", "room", "teacher", "lesson_type", "format")
        headings = {
            "pair": "Пара",
            "time": "Время",
            "subject": "Дисциплина",
            "room": "Ауд.",
            "teacher": "Преподаватель",
            "lesson_type": "Тип",
            "format": "Формат",
        }
        widths = {
            "pair": 55,
            "time": 110,
            "subject": 250,
            "room": 80,
            "teacher": 230,
            "lesson_type": 130,
            "format": 120,
        }

        visible = self._visible_schedule()
        for day in DAY_ORDER:
            tab = tk.Frame(notebook, bg=COLORS["frame"])
            notebook.add(tab, text=day)

            tree = ttk.Treeview(tab, columns=columns, show="headings", height=16)
            for key, title in headings.items():
                tree.heading(key, text=title)
                tree.column(key, width=widths[key], anchor="center" if key in {"pair", "room"} else "w")

            day_records = [item for item in visible if item["day"] == day]
            for item in day_records:
                tree.insert(
                    "",
                    "end",
                    values=(
                        item["pair"],
                        item["time"],
                        item["subject"],
                        self._room_text(item),
                        self._teacher_name(item["teacher_id"]),
                        item["lesson_type"],
                        self._format_text(item["format"]),
                    ),
                )
            tree.pack(fill="both", expand=True)

            if not day_records:
                tk.Label(
                    tab,
                    text="На этот день занятий нет.",
                    font=(FONT, 11),
                    bg=COLORS["frame"],
                    fg=COLORS["subtext"],
                ).place(relx=0.5, rely=0.5, anchor="center")

    def _visible_schedule(self) -> list[dict]:
        records = list(SCHEDULE_DATA)
        if self.current_user.role == "student" and self.current_user.student_id is not None:
            group = next(student["group"] for student in STUDENTS if student["id"] == self.current_user.student_id)
            records = [item for item in records if item["group"] == group]
        elif self.current_user.role == "teacher" and self.current_user.teacher_id is not None:
            records = [item for item in records if item["teacher_id"] == self.current_user.teacher_id]
        return sorted(records, key=lambda item: (DAY_ORDER[item["day"]], item["pair"], item["group"]))

    def _teacher_name(self, teacher_id: int) -> str:
        teacher = next(item for item in TEACHERS if item["id"] == teacher_id)
        return teacher["full_name"]

    def _room_text(self, item: dict) -> str:
        if item["format"] == "Дистанционная":
            return "-"
        return item["room"].split("-")[-1]

    def _format_text(self, value: str) -> str:
        return "Дистант" if value == "Дистанционная" else "Очно"

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

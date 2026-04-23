from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from data_sample import TEACHERS
from ui.theme import COLORS, FONT


class TeachersModule:
    def __init__(self, host_frame: tk.Frame) -> None:
        self.host_frame = host_frame
        self.tree: ttk.Treeview | None = None
        self.details_frame: tk.Frame | None = None

    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="ПРЕПОДАВАТЕЛИ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 6))
        tk.Label(
            self.host_frame,
            text="Раздел доступен только администратору и соответствует роли из модели виртуального деканата.",
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

        toolbar = tk.Frame(left, bg=COLORS["frame"])
        toolbar.pack(fill="x", pady=(0, 8))
        tk.Button(
            toolbar,
            text="Добавить преподавателя",
            font=(FONT, 10, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["bg"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._add_teacher_dialog,
        ).pack(side="right")

        columns = ("full_name", "department", "position", "degree")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        headings = {
            "full_name": "ФИО",
            "department": "Кафедра",
            "position": "Должность",
            "degree": "Степень",
        }
        widths = {
            "full_name": 220,
            "department": 220,
            "position": 150,
            "degree": 110,
        }
        for key, title in headings.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="w")

        for teacher in sorted(TEACHERS, key=lambda item: item["full_name"]):
            tree.insert(
                "",
                "end",
                iid=str(teacher["id"]),
                values=(teacher["full_name"], teacher["department"], teacher["position"], teacher["degree"]),
            )
        tree.bind("<<TreeviewSelect>>", self._on_select)
        tree.pack(fill="both", expand=True)
        self.tree = tree

        self._render_details(None)

    def _on_select(self, _event: object) -> None:
        if not self.tree:
            return
        selected = self.tree.selection()
        if not selected:
            self._render_details(None)
            return
        teacher = next(item for item in TEACHERS if item["id"] == int(selected[0]))
        self._render_details(teacher)

    def _render_details(self, teacher: dict | None) -> None:
        assert self.details_frame is not None
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        box = tk.Frame(self.details_frame, bg=COLORS["bg"])
        box.pack(fill="both", expand=True, padx=12, pady=12)

        if teacher is None:
            tk.Label(
                box,
                text="Выберите преподавателя для просмотра карточки.",
                wraplength=280,
                justify="left",
                font=(FONT, 10),
                bg=COLORS["bg"],
                fg=COLORS["subtext"],
            ).pack(anchor="w")
            return

        tk.Label(
            box,
            text=teacher["full_name"],
            font=(FONT, 13, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["accent"],
            wraplength=280,
            justify="left",
        ).pack(anchor="w")

        info = [
            f"Кафедра: {teacher['department']}",
            f"Должность: {teacher['position']}",
            f"Степень: {teacher['degree']}",
            f"Email: {teacher['email']}",
            f"Телефон: {teacher['phone']}",
            f"Дисциплины: {', '.join(teacher['subjects'])}",
        ]
        tk.Label(
            box,
            text="\n".join(info),
            justify="left",
            wraplength=280,
            font=(FONT, 10),
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(10, 12))

        tk.Button(
            box,
            text="Изменить email",
            font=(FONT, 10),
            bg=COLORS["button"],
            fg=COLORS["text"],
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=lambda: self._edit_email_dialog(teacher),
        ).pack(anchor="w")

    def _add_teacher_dialog(self) -> None:
        dialog = tk.Toplevel(self.host_frame)
        dialog.title("Добавление преподавателя")
        dialog.configure(bg=COLORS["frame"])
        dialog.resizable(False, False)

        full_name = tk.StringVar()
        department = tk.StringVar()
        position = tk.StringVar()
        degree = tk.StringVar(value="без степени")
        email = tk.StringVar()
        phone = tk.StringVar()

        rows = [
            ("ФИО", full_name),
            ("Кафедра", department),
            ("Должность", position),
            ("Степень", degree),
            ("Email", email),
            ("Телефон", phone),
        ]
        for idx, (title, variable) in enumerate(rows):
            tk.Label(dialog, text=title, bg=COLORS["frame"], fg=COLORS["text"], font=(FONT, 10)).grid(row=idx, column=0, sticky="w", padx=12, pady=6)
            tk.Entry(dialog, textvariable=variable, width=36).grid(row=idx, column=1, padx=12, pady=6)

        def save() -> None:
            if not full_name.get().strip() or not department.get().strip():
                messagebox.showerror("Преподаватели", "Заполните ФИО и кафедру.")
                return
            new_id = max(item["id"] for item in TEACHERS) + 1
            TEACHERS.append(
                {
                    "id": new_id,
                    "full_name": full_name.get().strip(),
                    "department": department.get().strip(),
                    "position": position.get().strip() or "Преподаватель",
                    "degree": degree.get().strip() or "без степени",
                    "email": email.get().strip() or f"teacher{new_id}@vdekanat.local",
                    "phone": phone.get().strip() or "79000000000",
                    "subjects": [],
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
        ).grid(row=len(rows), column=0, columnspan=2, pady=12)

    def _edit_email_dialog(self, teacher: dict) -> None:
        dialog = tk.Toplevel(self.host_frame)
        dialog.title("Изменение email")
        dialog.configure(bg=COLORS["frame"])
        dialog.resizable(False, False)

        value = tk.StringVar(value=teacher["email"])
        tk.Label(dialog, text=teacher["full_name"], bg=COLORS["frame"], fg=COLORS["accent"], font=(FONT, 11, "bold")).pack(padx=12, pady=(12, 8))
        tk.Entry(dialog, textvariable=value, width=40).pack(padx=12, pady=8)

        def save() -> None:
            new_value = value.get().strip()
            if not new_value:
                messagebox.showerror("Преподаватели", "Email не может быть пустым.")
                return
            teacher["email"] = new_value
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
        ).pack(pady=(4, 12))

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

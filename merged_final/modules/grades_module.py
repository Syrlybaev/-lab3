from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from data_sample import GRADES_DATA
from services.auth import SessionUser
from ui.theme import COLORS, FONT


class GradesModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser, current_semester: str = "2026 - весна") -> None:
        self.host_frame = host_frame
        self.current_user = current_user
        self.current_semester = current_semester
        self.grades_tree: ttk.Treeview | None = None
        self.semester_var: tk.StringVar | None = None
        self.rating_frame: tk.Frame | None = None
        self.dataset_name = self.current_user.full_name if self.current_user.full_name in GRADES_DATA else None

    def render(self) -> None:
        self._clear()
        tk.Label(self.host_frame, text="МОДУЛЬНЫЙ ЖУРНАЛ", font=(FONT, 18, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(10, 5))

        if self.dataset_name is None:
            tk.Label(self.host_frame, text="Для этой роли персональная ведомость не заведена. Открыта демонстрационная ведомость студента Смирнова Е.А.", font=(FONT, 10), bg=COLORS["frame"], fg=COLORS["subtext"], wraplength=760).pack(pady=(0, 12))
            self.dataset_name = next(iter(GRADES_DATA.keys()))

        semester_frame = tk.Frame(self.host_frame, bg=COLORS["frame"])
        semester_frame.pack(pady=(5, 15))
        tk.Label(semester_frame, text="Семестр:", font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["subtext"]).pack(side="left", padx=5)

        self.semester_var = tk.StringVar(value=self.current_semester)
        combo = ttk.Combobox(semester_frame, textvariable=self.semester_var, values=list(GRADES_DATA.keys()), state="readonly", width=15, font=(FONT, 10))
        combo.pack(side="left", padx=5)
        combo.bind("<<ComboboxSelected>>", lambda _: self.load_grades())

        columns = ("subject", "m1", "m2", "credit", "exam", "coefficient")
        tree = ttk.Treeview(self.host_frame, columns=columns, show="headings", height=15)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLORS["bg"], foreground=COLORS["text"], fieldbackground=COLORS["bg"], font=(FONT, 10))
        style.configure("Treeview.Heading", background=COLORS["button"], foreground=COLORS["text"], font=(FONT, 10, "bold"))

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
        tree.pack(fill="both", expand=True, pady=(0, 15))
        self.grades_tree = tree
        self.load_grades()

    def load_grades(self) -> None:
        if self.grades_tree is None or self.semester_var is None:
            return
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        semester_data = GRADES_DATA.get(self.semester_var.get(), [])
        total_weighted = 0.0
        total_coeff = 0.0
        for item in semester_data:
            m1_val = item["m1"] if item["m1"] is not None else "—"
            m2_val = item["m2"] if item["m2"] is not None else "—"
            if item["credit"] is not None:
                credit_val = str(item["credit"])
                total_weighted += item["credit"] * item["coefficient"]
                total_coeff += item["coefficient"]
            else:
                credit_val = "—"
            if item["exam"] is not None:
                exam_val = str(item["exam"])
                if item["m1"] is not None and item["m2"] is not None:
                    avg_exam = (item["m1"] + item["m2"] + item["exam"]) / 3
                    total_weighted += avg_exam * item["coefficient"]
                    total_coeff += item["coefficient"]
            else:
                exam_val = "—"
            self.grades_tree.insert("", "end", values=(item["subject"], m1_val, m2_val, credit_val, exam_val, f"{item['coefficient']:.1f}"))
        avg_rating = round(total_weighted / total_coeff, 1) if total_coeff > 0 else 0
        if self.rating_frame is not None and self.rating_frame.winfo_exists():
            self.rating_frame.destroy()
        self.rating_frame = tk.Frame(self.host_frame, bg=COLORS["frame"])
        self.rating_frame.pack(fill="x", pady=15, side="bottom")
        tk.Label(self.rating_frame, text=f"СРЕДНИЙ РЕЙТИНГ: {avg_rating}", font=(FONT, 14, "bold"), bg=COLORS["frame"], fg=COLORS["success"]).pack()

    def render_stub(self, title: str, text: str) -> None:
        self._clear()
        tk.Label(self.host_frame, text=title, font=(FONT, 18, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(30, 20))
        tk.Label(self.host_frame, text=text, font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["text"], wraplength=760).pack()

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

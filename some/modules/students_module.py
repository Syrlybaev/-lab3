from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from services.auth import SessionUser
from services.database import DatabaseService
from ui.theme import COLORS, FONT

ALL_GROUPS = ["ИДБ-23-13", "ИДБ-23-14", "ИДБ-23-15"]
STUDY_FORMS = ["Очная", "Заочная"]
FUNDINGS    = ["Бюджет", "Контракт"]
STATUSES    = ["Обучается", "Академический отпуск", "Отчислен"]


class StudentsModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser) -> None:
        self.host_frame = host_frame
        self.current_user = current_user
        self.db = DatabaseService()
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
        ).pack(pady=(15, 4))

        # Toolbar
        toolbar = tk.Frame(self.host_frame, bg=COLORS["frame"])
        toolbar.pack(fill="x", padx=14, pady=(0, 6))
        tk.Label(toolbar, text=self._intro_text(), font=(FONT, 11),
                 bg=COLORS["frame"], fg=COLORS["subtext"]).pack(side="left")
        tk.Button(
            toolbar, text="➕ Добавить студента",
            font=(FONT, 10, "bold"), bg=COLORS["accent"], fg=COLORS["bg"],
            relief="flat", padx=10, pady=5, cursor="hand2",
            command=self._add_student_dialog,
        ).pack(side="right")

        content = tk.Frame(self.host_frame, bg=COLORS["frame"])
        content.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        left = tk.Frame(content, bg=COLORS["frame"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(content, bg=COLORS["bg"], width=340)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self.details_frame = right

        cols   = ("full_name", "group", "record_book", "funding", "status")
        heads  = {"full_name":"ФИО", "group":"Группа", "record_book":"Зачет. книжка", "funding":"Основа", "status":"Статус"}
        widths = {"full_name":230, "group":100, "record_book":130, "funding":100, "status":145}

        tree = ttk.Treeview(left, columns=cols, show="headings", height=22)
        for key, title in heads.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="w")

        sb = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for s in self._visible_students():
            tree.insert("", "end", iid=str(s["id"]),
                        values=(s["full_name"], s["group"], s["record_book"], s["funding"], s["status"]))
        tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree = tree
        self._render_details(None)

    def _visible_students(self) -> list[dict]:
        students = self.db.get_students()
        if self.current_user.role == "teacher" and self.current_user.teacher_id is not None:
            groups = {r["study_group"] for r in self.db.get_schedule() if r["teacher_id"] == self.current_user.teacher_id}
            students = [s for s in students if s["study_group"] in groups]
        # Для совместимости переименовываем study_group в group если нужно, или просто используем s['study_group']
        for s in students:
            s['group'] = s['study_group']
        return sorted(students, key=lambda s: (s["study_group"], s["full_name"]))

    def _intro_text(self) -> str:
        count = len(self.db.get_students())
        if self.current_user.role == "teacher":
            return "Студенты ваших групп"
        return f"Всего студентов: {count}"

    def _on_select(self, _event: object) -> None:
        if not self.tree:
            return
        sel = self.tree.selection()
        if not sel:
            self._render_details(None)
            return
        
        student_id = int(sel[0])
        student = next((s for s in self.db.get_students() if s["id"] == student_id), None)
        if student:
            student['group'] = student['study_group']
        self._render_details(student)

    def _render_details(self, student: dict | None) -> None:
        assert self.details_frame is not None
        for w in self.details_frame.winfo_children():
            w.destroy()
        box = tk.Frame(self.details_frame, bg=COLORS["bg"])
        box.pack(fill="both", expand=True, padx=14, pady=14)

        if student is None:
            tk.Label(box, text="Выберите студента для просмотра карточки.",
                     wraplength=290, justify="left", font=(FONT, 10),
                     bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")
            return

        tk.Label(box, text=student["full_name"], font=(FONT, 13, "bold"),
                 bg=COLORS["bg"], fg=COLORS["accent"], wraplength=290, justify="left").pack(anchor="w")

        average = self._student_average(student["id"])
        info = [
            f"Группа:          {student['group']}",
            f"Зачёт. книжка:   {student['record_book']}",
            f"Курс:             {student['course']}",
            f"Направление:     {student['program']}",
            f"Форма обучения:  {student['study_form']}",
            f"Основа:          {student['funding']}",
            f"Статус:          {student['status']}",
            f"Средний балл:    {average:.1f}",
        ]
        tk.Label(box, text="\n".join(info), justify="left", wraplength=300,
                 font=(FONT, 10), bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(10, 0))

    def _student_average(self, student_id: int) -> float:
        grades = [r["m1"] + r["m2"] for r in self.db.get_grades() if r["student_id"] == student_id]
        return sum(grades) / len(grades) if grades else 0.0

    def _add_student_dialog(self) -> None:
        dlg = tk.Toplevel(self.host_frame)
        dlg.title("Добавление студента")
        dlg.configure(bg=COLORS["frame"])
        dlg.resizable(False, False)

        full_name   = tk.StringVar()
        group_var   = tk.StringVar(value=ALL_GROUPS[0])
        rec_book    = tk.StringVar()
        study_form  = tk.StringVar(value="Очная")
        funding     = tk.StringVar(value="Бюджет")
        status      = tk.StringVar(value="Обучается")

        rows = [
            ("ФИО",             full_name,  "entry"),
            ("Группа",          group_var,  "combo_grp"),
            ("Зачётная книжка", rec_book,   "entry"),
            ("Форма обучения",  study_form, "combo_sf"),
            ("Основа",          funding,    "combo_fn"),
            ("Статус",          status,     "combo_st"),
        ]
        for idx, (lbl, var, ftype) in enumerate(rows):
            tk.Label(dlg, text=lbl, font=(FONT, 10), bg=COLORS["frame"], fg=COLORS["text"]).grid(row=idx, column=0, sticky="w", padx=14, pady=6)
            if ftype == "entry":
                tk.Entry(dlg, textvariable=var, width=34).grid(row=idx, column=1, padx=14, pady=6)
            elif ftype == "combo_grp":
                ttk.Combobox(dlg, textvariable=var, state="readonly", width=31, values=ALL_GROUPS).grid(row=idx, column=1, padx=14, pady=6)
            elif ftype == "combo_sf":
                ttk.Combobox(dlg, textvariable=var, state="readonly", width=31, values=STUDY_FORMS).grid(row=idx, column=1, padx=14, pady=6)
            elif ftype == "combo_fn":
                ttk.Combobox(dlg, textvariable=var, state="readonly", width=31, values=FUNDINGS).grid(row=idx, column=1, padx=14, pady=6)
            elif ftype == "combo_st":
                ttk.Combobox(dlg, textvariable=var, state="readonly", width=31, values=STATUSES).grid(row=idx, column=1, padx=14, pady=6)

        def save() -> None:
            if not full_name.get().strip():
                messagebox.showerror("Студенты", "Введите ФИО студента.")
                return
            # Сохраняем в базу через DatabaseService
            data = {
                "full_name":   full_name.get().strip(),
                "group":       group_var.get(),
                "record_book": rec_book.get().strip() or f"23-XX-{len(self.db.get_students())+1:03d}",
                "course":      3,
                "program":     "Информационные системы и технологии",
                "study_form":  study_form.get(),
                "funding":     funding.get(),
                "status":      status.get(),
            }
            self.db.add_student(data)
            dlg.destroy()
            self.render()

        tk.Button(dlg, text="Сохранить", command=save,
                  bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=6,
                  ).grid(row=len(rows), column=0, columnspan=2, pady=12)

    def _clear(self) -> None:
        for w in self.host_frame.winfo_children():
            w.destroy()

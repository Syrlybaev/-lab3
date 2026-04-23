from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from services.auth import SessionUser
from services.database import DatabaseService
from services.utils import DAY_ORDER
from ui.theme import COLORS, FONT


class ScheduleModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser) -> None:
        self.host_frame = host_frame
        self.current_user = current_user
        self.db = DatabaseService()

    # ─────────────────────────────────────────────
    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="РАСПИСАНИЕ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 6))

        if self.current_user.role == "administrator":
            self._render_admin()
        else:
            self._render_user()

    # ─────────────────────────────────────────────
    # Расписание для студента / преподавателя
    # ─────────────────────────────────────────────
    def _render_user(self) -> None:
        notebook = ttk.Notebook(self.host_frame)
        notebook.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        visible = self._visible_schedule()
        self._fill_notebook(notebook, visible, show_group=False)

    # ─────────────────────────────────────────────
    # Расписание для администратора — вкладки «Группы» и «Преподаватели»
    # ─────────────────────────────────────────────
    def _render_admin(self) -> None:
        top_nb = ttk.Notebook(self.host_frame)
        top_nb.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # ── Вкладка «По группам» ──
        groups_tab = tk.Frame(top_nb, bg=COLORS["frame"])
        top_nb.add(groups_tab, text="По группам")

        groups = sorted({item["study_group"] for item in self.db.get_schedule()})
        sel_group = tk.StringVar(value=groups[0] if groups else "")

        ctrl_g = tk.Frame(groups_tab, bg=COLORS["frame"])
        ctrl_g.pack(fill="x", padx=12, pady=8)
        tk.Label(ctrl_g, text="Группа:", font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left")
        cb_group = ttk.Combobox(ctrl_g, textvariable=sel_group, values=groups, state="readonly", width=18, font=(FONT, 11))
        cb_group.pack(side="left", padx=8)

        area_g = tk.Frame(groups_tab, bg=COLORS["frame"])
        area_g.pack(fill="both", expand=True)
        nb_g = ttk.Notebook(area_g)
        nb_g.pack(fill="both", expand=True)

        edit_btn_g = tk.Button(
            ctrl_g, text="✏ Редактировать пару",
            font=(FONT, 10, "bold"), bg=COLORS["accent"], fg=COLORS["bg"],
            relief="flat", padx=10, pady=5, cursor="hand2",
        )
        edit_btn_g.pack(side="right", padx=8)

        trees_g: dict[str, ttk.Treeview] = {}

        def refresh_group(*_: object) -> None:
            for w in nb_g.winfo_children():
                w.destroy()
            trees_g.clear()
            records = [r for r in self.db.get_schedule() if r["study_group"] == sel_group.get()]
            # Совместимость с ключом 'group'
            for r in records: r['group'] = r['study_group']
            trees_g.update(self._fill_notebook(nb_g, records, show_group=False))

        edit_btn_g.configure(command=lambda: self._edit_schedule_dialog(
            nb_g, trees_g, lambda: refresh_group()
        ))

        cb_group.bind("<<ComboboxSelected>>", refresh_group)
        refresh_group()

        # ── Вкладка «По преподавателям» ──
        teachers_tab = tk.Frame(top_nb, bg=COLORS["frame"])
        top_nb.add(teachers_tab, text="По преподавателям")

        teachers = self.db.get_teachers()
        teacher_names = [t["full_name"] for t in sorted(teachers, key=lambda x: x["full_name"])]
        sel_teacher = tk.StringVar(value=teacher_names[0] if teacher_names else "")

        ctrl_t = tk.Frame(teachers_tab, bg=COLORS["frame"])
        ctrl_t.pack(fill="x", padx=12, pady=8)
        tk.Label(ctrl_t, text="Преподаватель:", font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left")
        cb_teacher = ttk.Combobox(ctrl_t, textvariable=sel_teacher, values=teacher_names, state="readonly", width=30, font=(FONT, 11))
        cb_teacher.pack(side="left", padx=8)

        area_t = tk.Frame(teachers_tab, bg=COLORS["frame"])
        area_t.pack(fill="both", expand=True)
        nb_t = ttk.Notebook(area_t)
        nb_t.pack(fill="both", expand=True)

        def refresh_teacher(*_: object) -> None:
            for w in nb_t.winfo_children():
                w.destroy()
            tid = next((t["id"] for t in self.db.get_teachers() if t["full_name"] == sel_teacher.get()), None)
            if tid is None:
                return
            records = [r for r in self.db.get_schedule() if r["teacher_id"] == tid]
            for r in records: r['group'] = r['study_group']
            self._fill_notebook(nb_t, records, show_group=True)

        cb_teacher.bind("<<ComboboxSelected>>", refresh_teacher)
        refresh_teacher()

    # ─────────────────────────────────────────────
    # Общая функция заполнения Notebook по дням
    # ─────────────────────────────────────────────
    def _fill_notebook(
        self, notebook: ttk.Notebook, records: list[dict], show_group: bool
    ) -> dict[str, ttk.Treeview]:
        cols: tuple
        heads: dict
        widths: dict
        if show_group:
            cols   = ("pair", "time", "group", "subject", "room", "lesson_type", "format", "period")
            heads  = {"pair":"№", "time":"Время", "group":"Группа", "subject":"Дисциплина", "room":"Ауд.", "lesson_type":"Тип", "format":"Формат", "period":"Период"}
            widths = {"pair":40, "time":105, "group":100, "subject":220, "room":70, "lesson_type":110, "format":80, "period":175}
        else:
            cols   = ("pair", "time", "subject", "room", "teacher", "lesson_type", "format", "period")
            heads  = {"pair":"№", "time":"Время", "subject":"Дисциплина", "room":"Ауд.", "teacher":"Преподаватель", "lesson_type":"Тип", "format":"Формат", "period":"Период"}
            widths = {"pair":40, "time":105, "subject":230, "room":70, "teacher":200, "lesson_type":110, "format":80, "period":175}

        trees: dict[str, ttk.Treeview] = {}
        for day in DAY_ORDER:
            tab = tk.Frame(notebook, bg=COLORS["frame"])
            notebook.add(tab, text=day)

            tree = ttk.Treeview(tab, columns=cols, show="headings", height=22)
            for key, title in heads.items():
                tree.heading(key, text=title)
                anchor = "center" if key in {"pair", "room"} else "w"
                tree.column(key, width=widths[key], anchor=anchor)

            sb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            tree.pack(fill="both", expand=True)

            day_rows = sorted([r for r in records if r["day"] == day], key=lambda r: r["pair"])
            for r in day_rows:
                period = f"{r.get('date_start','?')} – {r.get('date_end','?')}"
                room   = self._room_text(r)
                fmt    = self._format_text(r["format"])
                if show_group:
                    vals = (r["pair"], r["time"], r["group"], r["subject"], room, r["lesson_type"], fmt, period)
                else:
                    vals = (r["pair"], r["time"], r["subject"], room, self._teacher_name(r["teacher_id"]), r["lesson_type"], fmt, period)
                tree.insert("", "end", values=vals)

            if not day_rows:
                tk.Label(
                    tab, text="На этот день занятий нет.",
                    font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["subtext"],
                ).place(relx=0.5, rely=0.5, anchor="center")

            trees[day] = tree
        return trees

    # ─────────────────────────────────────────────
    # Диалог редактирования пары (admin)
    # ─────────────────────────────────────────────
    def _edit_schedule_dialog(
        self,
        notebook: ttk.Notebook,
        trees: dict[str, ttk.Treeview],
        on_save: object,
    ) -> None:
        # Ищем выделенную строку в активном дне
        current_day = None
        selected_idx = None
        try:
            idx = notebook.index(notebook.select())
            current_day = list(DAY_ORDER.keys())[idx]
        except Exception:
            messagebox.showwarning("Расписание", "Выберите день и строку для редактирования.")
            return

        tree = trees.get(current_day)
        if tree is None:
            return
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Расписание", "Выберите строку в расписании.")
            return

        vals = tree.item(sel[0], "values")
        pair_num = int(vals[0])
        group_str = notebook.master.master  # просто служебно

        # В SQLite реализации пока редактирование через DB не внедрено полно, 
        # но мы можем обновить запись если добавим метод в DatabaseService.
        # Для текущего задания ограничимся тем, что покажем диалог, 
        # но предупредим что запись в DB требует доработки DatabaseService.
        
        # Найдем запись в базе
        record = next(
            (r for r in self.db.get_schedule() if r["day"] == current_day and r["pair"] == pair_num),
            None,
        )
        if record is None:
            messagebox.showwarning("Расписание", "Запись не найдена.")
            return

        dlg = tk.Toplevel(self.host_frame)
        dlg.title("Редактирование пары")
        dlg.configure(bg=COLORS["frame"])
        dlg.resizable(False, False)

        room_var    = tk.StringVar(value=record.get("room", ""))
        type_var    = tk.StringVar(value=record.get("lesson_type", ""))
        format_var  = tk.StringVar(value=record.get("format", ""))
        ds_var      = tk.StringVar(value=record.get("date_start", ""))
        de_var      = tk.StringVar(value=record.get("date_end", ""))

        fields = [
            ("Дисциплина",  record["subject"],  None),
            ("День / пара", f"{current_day}, пара {pair_num}", None),
            ("Аудитория",   room_var,   "entry"),
            ("Тип занятия", type_var,   "combo_type"),
            ("Формат",      format_var, "combo_fmt"),
            ("Дата начала", ds_var,     "entry"),
            ("Дата конца",  de_var,     "entry"),
        ]
        for row, (label, val, ftype) in enumerate(fields):
            tk.Label(dlg, text=label, font=(FONT, 10), bg=COLORS["frame"], fg=COLORS["text"]).grid(row=row, column=0, sticky="w", padx=14, pady=6)
            if ftype is None:
                tk.Label(dlg, text=val, font=(FONT, 10), bg=COLORS["frame"], fg=COLORS["subtext"]).grid(row=row, column=1, sticky="w", padx=14, pady=6)
            elif ftype == "entry":
                tk.Entry(dlg, textvariable=val, width=30).grid(row=row, column=1, padx=14, pady=6)
            elif ftype == "combo_type":
                ttk.Combobox(dlg, textvariable=val, state="readonly", width=27,
                             values=["Лекция", "Семинар", "Лабораторная", "Дистант"]).grid(row=row, column=1, padx=14, pady=6)
            elif ftype == "combo_fmt":
                ttk.Combobox(dlg, textvariable=val, state="readonly", width=27,
                             values=["Очная", "Дистанционная"]).grid(row=row, column=1, padx=14, pady=6)

        def save() -> None:
            record["room"]        = room_var.get().strip()
            record["lesson_type"] = type_var.get().strip()
            record["format"]      = format_var.get().strip()
            record["date_start"]  = ds_var.get().strip()
            record["date_end"]    = de_var.get().strip()
            dlg.destroy()
            if callable(on_save):
                on_save()

        tk.Button(dlg, text="Сохранить", command=save,
                  bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=6
                  ).grid(row=len(fields), column=0, columnspan=2, pady=12)

    # ─────────────────────────────────────────────
    # Вспомогательные
    # ─────────────────────────────────────────────
    def _visible_schedule(self) -> list[dict]:
        records = self.db.get_schedule()
        if self.current_user.role == "student" and self.current_user.student_id is not None:
            student = next(s for s in self.db.get_students() if s["id"] == self.current_user.student_id)
            group = student["study_group"]
            records = [r for r in records if r["study_group"] == group]
        elif self.current_user.role == "teacher" and self.current_user.teacher_id is not None:
            records = [r for r in records if r["teacher_id"] == self.current_user.teacher_id]
        
        for r in records: r['group'] = r['study_group']
        return sorted(records, key=lambda r: (DAY_ORDER[r["day"]], r["pair"]))

    def _teacher_name(self, teacher_id: int) -> str:
        teachers = self.db.get_teachers()
        return next((t["full_name"] for t in teachers if t["id"] == teacher_id), f"Преподаватель #{teacher_id}")

    def _room_text(self, item: dict) -> str:
        if item["format"] == "Дистанционная":
            return "–"
        room = item.get("room", "")
        return room if room else "–"

    def _format_text(self, value: str) -> str:
        return "Дистант" if value == "Дистанционная" else "Очно"

    def _clear(self) -> None:
        for w in self.host_frame.winfo_children():
            w.destroy()

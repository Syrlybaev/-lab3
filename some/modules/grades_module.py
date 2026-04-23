from data_sample import grade_label
from services.auth import SessionUser
from services.rbac import RBACService
from services.database import DatabaseService
from ui.theme import COLORS, FONT

SEMESTERS = ["2025 весна", "2025 осень", "2026 весна"]
ALL_GROUPS = ["ИДБ-23-13", "ИДБ-23-14", "ИДБ-23-15"]


def _all_subjects() -> list[str]:
    return sorted({r["subject"] for r in GRADE_RECORDS})


class GradesModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser, rbac: RBACService) -> None:
        self.host_frame = host_frame
        self.current_user = current_user
        self.rbac = rbac
        self.db = DatabaseService()
        self.tree: ttk.Treeview | None = None
        self._cache_students = {s['id']: s['full_name'] for s in self.db.get_students()}
        self._cache_teachers = {t['id']: t['full_name'] for t in self.db.get_teachers()}

    def _all_subjects(self):
        return sorted({r["subject"] for r in self.db.get_grades()})

    # ─────────────────────────────────────────────
    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="МОДУЛЬНЫЙ ЖУРНАЛ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 4))

        if self.current_user.role == "student":
            self._render_student()
        else:
            self._render_staff()

    # ─────────────────────────────────────────────
    # Студент — просто таблица своих оценок
    # ─────────────────────────────────────────────
    def _render_student(self) -> None:
        # Выбор семестра
        ctrl = tk.Frame(self.host_frame, bg=COLORS["frame"])
        ctrl.pack(fill="x", padx=14, pady=(0, 6))
        tk.Label(ctrl, text="Семестр:", font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left")
        sem_var = tk.StringVar(value=SEMESTERS[-1])
        cb_sem = ttk.Combobox(ctrl, textvariable=sem_var, values=SEMESTERS, state="readonly", width=16, font=(FONT, 11))
        cb_sem.pack(side="left", padx=8)

        table_frame = tk.Frame(self.host_frame, bg=COLORS["frame"])
        table_frame.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        def refresh(*_: object) -> None:
            for w in table_frame.winfo_children():
                w.destroy()
            records = [
                r for r in self.db.get_grades()
                if r["student_id"] == self.current_user.student_id
                and r["semester"] == sem_var.get()
            ]
            self._build_student_table(table_frame, records)

        cb_sem.bind("<<ComboboxSelected>>", refresh)
        refresh()

    def _build_student_table(self, parent: tk.Frame, records: list[dict]) -> None:
        cols   = ("subject", "control_type", "m1", "grade_m1", "m2", "grade_m2", "total", "status")
        heads  = {"subject":"Дисциплина", "control_type":"Форма контроля", "m1":"М1", "grade_m1":"Оценка М1",
                  "m2":"М2", "grade_m2":"Оценка М2", "total":"Итого", "status":"Статус"}
        widths = {"subject":280, "control_type":160, "m1":55, "grade_m1":100, "m2":55, "grade_m2":100, "total":65, "status":110}

        tree = ttk.Treeview(parent, columns=cols, show="headings", height=20)
        for key, title in heads.items():
            tree.heading(key, text=title)
            anchor = "center" if key in {"m1","m2","total"} else "w"
            tree.column(key, width=widths[key], anchor=anchor)

        for r in records:
            total = r["m1"] + r["m2"]
            tree.insert("", "end", iid=str(r["id"]), values=(
                r["subject"], r["control_type"],
                r["m1"], grade_label(r["m1"]),
                r["m2"], grade_label(r["m2"]),
                total, r["status"],
            ))

        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        self.tree = tree

        avg = sum(r["m1"] + r["m2"] for r in records) / max(len(records), 1)
        tk.Label(
            self.host_frame,
            text=f"Средний балл (M1+M2): {avg:.1f}",
            font=(FONT, 11, "bold"),
            bg=COLORS["frame"], fg=COLORS["success"],
        ).pack(anchor="w", padx=14, pady=(0, 8))

    # ─────────────────────────────────────────────
    # Преподаватель / Администратор — вкладки
    # ─────────────────────────────────────────────
    def _render_staff(self) -> None:
        can_edit = self.rbac.check(self.current_user.role, "grades", "edit").allowed

        # Панель фильтров
        ctrl = tk.Frame(self.host_frame, bg=COLORS["frame"])
        ctrl.pack(fill="x", padx=14, pady=(0, 6))

        tk.Label(ctrl, text="Семестр:", font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left")
        sem_var = tk.StringVar(value=SEMESTERS[-1])
        ttk.Combobox(ctrl, textvariable=sem_var, values=SEMESTERS, state="readonly", width=14, font=(FONT, 11)).pack(side="left", padx=6)

        tk.Label(ctrl, text="Дисциплина:", font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left", padx=(12, 0))
        subj_var = tk.StringVar(value="Все")
        subj_cb = ttk.Combobox(ctrl, textvariable=subj_var, values=["Все"] + _all_subjects(), state="readonly", width=26, font=(FONT, 11))
        subj_cb.pack(side="left", padx=6)

        refresh_btn = tk.Button(
            ctrl, text="Обновить", font=(FONT, 10, "bold"),
            bg=COLORS["button"], fg=COLORS["text"], relief="flat", padx=10, pady=4, cursor="hand2",
        )
        refresh_btn.pack(side="left", padx=8)

        if can_edit:
            edit_btn = tk.Button(
                ctrl, text="✏ Изменить оценку", font=(FONT, 10, "bold"),
                bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=10, pady=4, cursor="hand2",
                command=self._edit_selected_grade,
            )
            edit_btn.pack(side="right", padx=8)

        # Notebook по группам
        nb = ttk.Notebook(self.host_frame)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        group_trees: dict[str, ttk.Treeview] = {}

        def refresh(*_: object) -> None:
            for tab in nb.tabs():
                nb.forget(tab)
            group_trees.clear()

            sem  = sem_var.get()
            subj = subj_var.get()
            
            all_grades = self.db.get_grades()

            for grp in ALL_GROUPS:
                tab = tk.Frame(nb, bg=COLORS["frame"])
                nb.add(tab, text=grp)
                
                # Фильтруем студентов этой группы
                group_student_ids = [s['id'] for s in self.db.get_students() if s['study_group'] == grp]
                
                records = [
                    r for r in all_grades
                    if r["student_id"] in group_student_ids and r["semester"] == sem
                    and (subj == "Все" or r["subject"] == subj)
                ]
                # Добавляем инфо о группе в запись для совместимости
                for r in records: r['group'] = grp
                
                tree = self._build_staff_table(tab, records)
                group_trees[grp] = tree

        refresh_btn.configure(command=refresh)
        sem_var.trace_add("write", refresh)
        subj_var.trace_add("write", refresh)
        refresh()

    def _build_staff_table(self, parent: tk.Frame, records: list[dict]) -> ttk.Treeview:
        cols   = ("student", "subject", "control_type", "m1", "grade_m1", "m2", "grade_m2", "total", "teacher", "status")
        heads  = {
            "student":"Студент", "subject":"Дисциплина", "control_type":"Форма контроля",
            "m1":"М1", "grade_m1":"Оценка М1", "m2":"М2", "grade_m2":"Оценка М2",
            "total":"Итого", "teacher":"Преподаватель", "status":"Статус",
        }
        widths = {
            "student":185, "subject":185, "control_type":145,
            "m1":50, "grade_m1":90, "m2":50, "grade_m2":90,
            "total":60, "teacher":175, "status":105,
        }

        tree = ttk.Treeview(parent, columns=cols, show="headings", height=20)
        for key, title in heads.items():
            tree.heading(key, text=title)
            anchor = "center" if key in {"m1","m2","total"} else "w"
            tree.column(key, width=widths[key], anchor=anchor)

        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for r in records:
            total = r["m1"] + r["m2"]
            tree.insert("", "end", iid=str(r["id"]), values=(
                self._student_name(r["student_id"]),
                r["subject"], r["control_type"],
                r["m1"], grade_label(r["m1"]),
                r["m2"], grade_label(r["m2"]),
                total,
                self._teacher_name(r["teacher_id"]),
                r["status"],
            ))

        self.tree = tree
        return tree

    # ─────────────────────────────────────────────
    # Диалог редактирования M1 и M2 отдельно
    # ─────────────────────────────────────────────
    def _edit_selected_grade(self) -> None:
        if not self.tree:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Оценки", "Сначала выберите строку.")
            return

        grade = next((r for r in self.db.get_grades() if r["id"] == int(selected[0])), None)
        if grade is None:
            return
        
        # Доп. проверка прав: преподаватель может править только свои предметы
        if self.current_user.role == "teacher":
            if grade['teacher_id'] != self.current_user.teacher_id:
                messagebox.showerror("Доступ", "Вы можете редактировать оценки только по своим дисциплинам.")
                return

        dlg = tk.Toplevel(self.host_frame)
        dlg.title("Изменение оценки")
        dlg.configure(bg=COLORS["frame"])
        dlg.resizable(False, False)

        m1_var      = tk.StringVar(value=str(grade["m1"]))
        m2_var      = tk.StringVar(value=str(grade["m2"]))
        status_var  = tk.StringVar(value=grade["status"])
        comment_var = tk.StringVar(value="")

        info_rows = [
            ("Студент",        self._student_name(grade["student_id"])),
            ("Дисциплина",     grade["subject"]),
            ("Форма контроля", grade["control_type"]),
            ("Семестр",        grade["semester"]),
        ]
        for row, (lbl, val) in enumerate(info_rows):
            tk.Label(dlg, text=lbl,  font=(FONT, 10, "bold"), bg=COLORS["frame"], fg=COLORS["text"]).grid(row=row, column=0, sticky="w", padx=14, pady=5)
            tk.Label(dlg, text=val,  font=(FONT, 10),          bg=COLORS["frame"], fg=COLORS["subtext"]).grid(row=row, column=1, sticky="w", padx=14, pady=5)

        sep = len(info_rows)
        tk.Label(dlg, text="─" * 40, bg=COLORS["frame"], fg=COLORS["line"]).grid(row=sep, column=0, columnspan=2, pady=4)

        edit_rows = [
            ("М1 (25–54)", m1_var, "entry"),
            ("М2 (25–54)", m2_var, "entry"),
            ("Статус",     status_var, "combo"),
            ("Комментарий",comment_var, "entry"),
        ]
        for i, (lbl, var, ftype) in enumerate(edit_rows, start=sep + 1):
            tk.Label(dlg, text=lbl, font=(FONT, 10, "bold"), bg=COLORS["frame"], fg=COLORS["text"]).grid(row=i, column=0, sticky="w", padx=14, pady=5)
            if ftype == "entry":
                tk.Entry(dlg, textvariable=var, width=32).grid(row=i, column=1, padx=14, pady=5)
            else:
                ttk.Combobox(dlg, textvariable=var, state="readonly", width=29,
                             values=["Подтверждена", "Пересдача", "Неявка"]).grid(row=i, column=1, padx=14, pady=5)

        total_lbl = tk.Label(dlg, text="", font=(FONT, 11, "bold"), bg=COLORS["frame"], fg=COLORS["accent"])
        total_lbl.grid(row=sep + len(edit_rows) + 1, column=0, columnspan=2, pady=4)

        def update_total(*_: object) -> None:
            try:
                t = int(m1_var.get()) + int(m2_var.get())
                total_lbl.configure(text=f"Итоговый балл: {t}  ({grade_label(int(m1_var.get()))} / {grade_label(int(m2_var.get()))})")
            except ValueError:
                total_lbl.configure(text="Итоговый балл: —")

        m1_var.trace_add("write", update_total)
        m2_var.trace_add("write", update_total)
        update_total()

        def save() -> None:
            try:
                new_m1 = int(m1_var.get().strip())
                new_m2 = int(m2_var.get().strip())
            except ValueError:
                messagebox.showerror("Оценки", "М1 и М2 должны быть целыми числами.")
                return
            
            # Сохраняем в базу
            success = self.db.update_grade(
                grade_id=grade["id"],
                m1=new_m1,
                m2=new_m2,
                status=status_var.get(),
                changed_by=self.current_user.login,
                comment=comment_var.get().strip() or "Изменение через интерфейс"
            )
            
            if success:
                dlg.destroy()
                self.render()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить оценку в базе данных.")

        tk.Button(
            dlg, text="Сохранить", command=save,
            bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=6,
        ).grid(row=sep + len(edit_rows) + 2, column=0, columnspan=2, pady=12)

    # ─────────────────────────────────────────────
    # Вспомогательные
    # ─────────────────────────────────────────────
    def _visible_grades(self) -> list[dict]:
        records = list(GRADE_RECORDS)
        if self.current_user.role == "teacher" and self.current_user.teacher_id is not None:
            records = [r for r in records if r["teacher_id"] == self.current_user.teacher_id]
        return sorted(records, key=lambda r: (r["group"], r["student_id"], r["subject"]))

    def _student_name(self, student_id: int) -> str:
        s = next((s for s in STUDENTS if s["id"] == student_id), None)
        return s["full_name"] if s else f"Студент #{student_id}"

    def _teacher_name(self, teacher_id: int) -> str:
        t = next((t for t in TEACHERS if t["id"] == teacher_id), None)
        return t["full_name"] if t else f"Преподаватель #{teacher_id}"

    def _clear(self) -> None:
        for w in self.host_frame.winfo_children():
            w.destroy()

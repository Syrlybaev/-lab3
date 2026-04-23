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
        ).pack(pady=(15, 4))

        content = tk.Frame(self.host_frame, bg=COLORS["frame"])
        content.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        left = tk.Frame(content, bg=COLORS["frame"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(content, bg=COLORS["bg"], width=340)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self.details_frame = right

        # Toolbar
        toolbar = tk.Frame(left, bg=COLORS["frame"])
        toolbar.pack(fill="x", pady=(0, 8))
        tk.Button(
            toolbar, text="➕ Добавить",
            font=(FONT, 10, "bold"), bg=COLORS["accent"], fg=COLORS["bg"],
            relief="flat", padx=10, pady=5, cursor="hand2",
            command=self._add_teacher_dialog,
        ).pack(side="right")
        tk.Button(
            toolbar, text="🗑 Удалить",
            font=(FONT, 10, "bold"), bg=COLORS["error"], fg=COLORS["bg"],
            relief="flat", padx=10, pady=5, cursor="hand2",
            command=self._delete_teacher,
        ).pack(side="right", padx=(0, 8))
        tk.Label(toolbar, text=f"Всего: {len(TEACHERS)} преподавателей",
                 font=(FONT, 11), bg=COLORS["frame"], fg=COLORS["subtext"]).pack(side="left")

        cols   = ("full_name", "department", "position", "degree")
        heads  = {"full_name":"ФИО", "department":"Кафедра", "position":"Должность", "degree":"Степень"}
        widths = {"full_name":220, "department":240, "position":155, "degree":110}

        tree = ttk.Treeview(left, columns=cols, show="headings", height=22)
        for key, title in heads.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="w")

        sb = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for t in sorted(TEACHERS, key=lambda x: x["full_name"]):
            tree.insert("", "end", iid=str(t["id"]),
                        values=(t["full_name"], t["department"], t["position"], t["degree"]))
        tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree = tree
        self._render_details(None)

    def _on_select(self, _event: object) -> None:
        if not self.tree:
            return
        sel = self.tree.selection()
        teacher = next((t for t in TEACHERS if str(t["id"]) == sel[0]), None) if sel else None
        self._render_details(teacher)

    def _render_details(self, teacher: dict | None) -> None:
        assert self.details_frame is not None
        for w in self.details_frame.winfo_children():
            w.destroy()
        box = tk.Frame(self.details_frame, bg=COLORS["bg"])
        box.pack(fill="both", expand=True, padx=14, pady=14)

        if teacher is None:
            tk.Label(box, text="Выберите преподавателя для просмотра карточки.",
                     wraplength=290, justify="left", font=(FONT, 10),
                     bg=COLORS["bg"], fg=COLORS["subtext"]).pack(anchor="w")
            return

        tk.Label(box, text=teacher["full_name"], font=(FONT, 13, "bold"),
                 bg=COLORS["bg"], fg=COLORS["accent"], wraplength=290, justify="left").pack(anchor="w")

        info = [
            f"Кафедра:     {teacher['department']}",
            f"Должность:   {teacher['position']}",
            f"Степень:     {teacher['degree']}",
            f"Email:       {teacher['email']}",
            f"Телефон:     {teacher['phone']}",
            f"Дисциплины:\n  " + "\n  ".join(teacher["subjects"]),
        ]
        tk.Label(box, text="\n".join(info), justify="left", wraplength=300,
                 font=(FONT, 10), bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(10, 14))

        tk.Button(box, text="✉ Изменить email",
                  font=(FONT, 10), bg=COLORS["button"], fg=COLORS["text"],
                  relief="flat", padx=10, pady=5, cursor="hand2",
                  command=lambda: self._edit_email_dialog(teacher)).pack(anchor="w")

    def _delete_teacher(self) -> None:
        if not self.tree:
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Преподаватели", "Выберите преподавателя для удаления.")
            return
        teacher = next((t for t in TEACHERS if str(t["id"]) == sel[0]), None)
        if teacher is None:
            return
        if messagebox.askyesno("Удаление", f"Удалить преподавателя «{teacher['full_name']}»?"):
            TEACHERS.remove(teacher)
            self.render()

    def _add_teacher_dialog(self) -> None:
        dlg = tk.Toplevel(self.host_frame)
        dlg.title("Добавление преподавателя")
        dlg.configure(bg=COLORS["frame"])
        dlg.resizable(False, False)

        full_name  = tk.StringVar()
        department = tk.StringVar()
        position   = tk.StringVar()
        degree     = tk.StringVar(value="без степени")
        email      = tk.StringVar()
        phone      = tk.StringVar()

        rows = [
            ("ФИО",       full_name),
            ("Кафедра",   department),
            ("Должность", position),
            ("Степень",   degree),
            ("Email",     email),
            ("Телефон",   phone),
        ]
        for idx, (lbl, var) in enumerate(rows):
            tk.Label(dlg, text=lbl, font=(FONT, 10), bg=COLORS["frame"], fg=COLORS["text"]).grid(row=idx, column=0, sticky="w", padx=14, pady=6)
            tk.Entry(dlg, textvariable=var, width=36).grid(row=idx, column=1, padx=14, pady=6)

        def save() -> None:
            if not full_name.get().strip() or not department.get().strip():
                messagebox.showerror("Преподаватели", "Заполните ФИО и кафедру.")
                return
            new_id = max(t["id"] for t in TEACHERS) + 1 if TEACHERS else 1
            TEACHERS.append({
                "id":         new_id,
                "full_name":  full_name.get().strip(),
                "department": department.get().strip(),
                "position":   position.get().strip() or "Преподаватель",
                "degree":     degree.get().strip() or "без степени",
                "email":      email.get().strip() or f"teacher{new_id}@vdekanat.local",
                "phone":      phone.get().strip() or "79000000000",
                "subjects":   [],
            })
            dlg.destroy()
            self.render()

        tk.Button(dlg, text="Сохранить", command=save,
                  bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=6,
                  ).grid(row=len(rows), column=0, columnspan=2, pady=12)

    def _edit_email_dialog(self, teacher: dict) -> None:
        dlg = tk.Toplevel(self.host_frame)
        dlg.title("Изменение email")
        dlg.configure(bg=COLORS["frame"])
        dlg.resizable(False, False)

        value = tk.StringVar(value=teacher["email"])
        tk.Label(dlg, text=teacher["full_name"], font=(FONT, 11, "bold"),
                 bg=COLORS["frame"], fg=COLORS["accent"]).pack(padx=14, pady=(14, 8))
        tk.Entry(dlg, textvariable=value, width=40).pack(padx=14, pady=8)

        def save() -> None:
            new_val = value.get().strip()
            if not new_val:
                messagebox.showerror("Преподаватели", "Email не может быть пустым.")
                return
            teacher["email"] = new_val
            dlg.destroy()
            self.render()

        tk.Button(dlg, text="Сохранить", command=save,
                  bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=6,
                  ).pack(pady=(4, 14))

    def _clear(self) -> None:
        for w in self.host_frame.winfo_children():
            w.destroy()

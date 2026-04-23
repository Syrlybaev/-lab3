from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from data_sample import FINANCE_RECORDS, FINANCE_TYPES, STUDENTS
from services.auth import SessionUser
from ui.theme import COLORS, FONT

MONTHS = [
    "2026-01", "2026-02", "2026-03", "2026-04", "2026-05",
    "2025-09", "2025-10", "2025-11", "2025-12",
]
SEMESTERS = ["2024 весна", "2024 осень", "2025 весна", "2025 осень", "2026 весна"]


def _student_name(sid: int) -> str:
    s = next((s for s in STUDENTS if s["id"] == sid), None)
    return s["full_name"] if s else f"#{sid}"


def _balance(student_id: int) -> float:
    total = 0.0
    for r in FINANCE_RECORDS:
        if r["student_id"] == student_id:
            if r["sign"] == 1:
                total += r["amount"]
            else:
                total -= r["amount"] if r["status"] == "Оплачено" or r["status"] == "Выплачено" else 0
    return total


class FinanceModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser) -> None:
        self.host_frame = host_frame
        self.current_user = current_user

    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="БУХГАЛТЕРИЯ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 6))

        if self.current_user.role == "student":
            self._render_student()
        else:
            self._render_staff()

    # ─────────────────────────────────────────────
    # СТУДЕНТ — личный финансовый кабинет
    # ─────────────────────────────────────────────
    def _render_student(self) -> None:
        sid = self.current_user.student_id
        if sid is None:
            return

        receipts = sum(r["amount"] for r in FINANCE_RECORDS if r["student_id"] == sid and r["sign"] == 1 and r["status"] == "Выплачено")
        payments = sum(r["amount"] for r in FINANCE_RECORDS if r["student_id"] == sid and r["sign"] == -1 and r["status"] == "Оплачено")
        balance  = receipts - payments

        # ── Карточка баланса ──
        card = tk.Frame(self.host_frame, bg=COLORS["bg"], highlightthickness=1, highlightbackground=COLORS["line"])
        card.pack(fill="x", padx=20, pady=(0, 12))
        bal_color = COLORS["success"] if balance >= 0 else COLORS["error"]
        tk.Label(card, text=f"Баланс:  {balance:+,.0f} ₸",
                 font=(FONT, 16, "bold"), bg=COLORS["bg"], fg=bal_color).pack(pady=(14, 4))
        tk.Label(card,
                 text=f"Начислено стипендий / соцвыплат: {receipts:,.0f} ₸     Оплачено: {payments:,.0f} ₸",
                 font=(FONT, 10), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(pady=(0, 14))

        # ── Кнопки оплаты ──
        btns = tk.Frame(self.host_frame, bg=COLORS["frame"])
        btns.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(btns, text="💳 Оплатить обучение",
                  font=(FONT, 11, "bold"), bg=COLORS["accent"], fg=COLORS["bg"],
                  relief="flat", padx=14, pady=8, cursor="hand2",
                  command=lambda: self._pay_tuition_dialog(sid)).pack(side="left", padx=(0, 10))
        tk.Button(btns, text="🏠 Оплатить общежитие",
                  font=(FONT, 11, "bold"), bg=COLORS["button"], fg=COLORS["text"],
                  relief="flat", padx=14, pady=8, cursor="hand2",
                  command=lambda: self._pay_dorm_dialog(sid)).pack(side="left")

        # ── Таблица операций ──
        tk.Label(self.host_frame, text="История операций",
                 font=(FONT, 12, "bold"), bg=COLORS["frame"], fg=COLORS["text"]).pack(anchor="w", padx=20, pady=(6, 4))

        cols   = ("date", "op_type", "amount", "period", "status", "comment")
        heads  = {"date":"Дата", "op_type":"Тип операции", "amount":"Сумма, ₸", "period":"Период", "status":"Статус", "comment":"Комментарий"}
        widths = {"date":100, "op_type":200, "amount":110, "period":110, "status":110, "comment":280}

        frame = tk.Frame(self.host_frame, bg=COLORS["frame"])
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for key, title in heads.items():
            tree.heading(key, text=title)
            anchor = "e" if key == "amount" else "w"
            tree.column(key, width=widths[key], anchor=anchor)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        records = sorted(
            [r for r in FINANCE_RECORDS if r["student_id"] == sid],
            key=lambda r: r["date"], reverse=True,
        )
        for r in records:
            sign_str = "+" if r["sign"] == 1 else "–"
            tree.insert("", "end", values=(
                r["date"],
                FINANCE_TYPES.get(r["op_type"], r["op_type"]),
                f"{sign_str}{r['amount']:,.0f}",
                r["period"],
                r["status"],
                r["comment"],
            ))

    # ── Диалог оплаты обучения ──
    def _pay_tuition_dialog(self, sid: int) -> None:
        dlg = tk.Toplevel(self.host_frame)
        dlg.title("Оплата обучения")
        dlg.configure(bg=COLORS["frame"])
        dlg.resizable(False, False)

        sem_var = tk.StringVar(value=SEMESTERS[-1])
        amt_var = tk.StringVar(value="95000")
        tk.Label(dlg, text="Оплата обучения", font=(FONT, 13, "bold"),
                 bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(14, 8), padx=20)
        for lbl, var, vals in [("Семестр", sem_var, SEMESTERS), ("Сумма, ₸", amt_var, None)]:
            row = tk.Frame(dlg, bg=COLORS["frame"])
            row.pack(fill="x", padx=20, pady=4)
            tk.Label(row, text=lbl, width=14, anchor="w", font=(FONT, 10),
                     bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left")
            if vals:
                ttk.Combobox(row, textvariable=var, values=vals, state="readonly", width=22).pack(side="left")
            else:
                tk.Entry(row, textvariable=var, width=24).pack(side="left")

        def confirm() -> None:
            try:
                amount = float(amt_var.get().replace(",", ""))
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму.")
                return
            new_id = max(r["id"] for r in FINANCE_RECORDS) + 1
            FINANCE_RECORDS.append({
                "id": new_id, "student_id": sid, "op_type": "tuition",
                "amount": amount, "period": sem_var.get(), "date": "2026-04-23",
                "status": "Оплачено", "sign": -1, "comment": f"Оплата обучения {sem_var.get()} (симуляция)",
            })
            messagebox.showinfo("Оплата", f"Оплата {amount:,.0f} ₸ за {sem_var.get()} успешно проведена (симуляция).")
            dlg.destroy()
            self.render()

        tk.Button(dlg, text="Подтвердить оплату", command=confirm,
                  bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=8).pack(pady=14)

    # ── Диалог оплаты общежития ──
    def _pay_dorm_dialog(self, sid: int) -> None:
        dlg = tk.Toplevel(self.host_frame)
        dlg.title("Оплата общежития")
        dlg.configure(bg=COLORS["frame"])
        dlg.resizable(False, False)

        month_var = tk.StringVar(value=MONTHS[0])
        amt_var   = tk.StringVar(value="3500")
        tk.Label(dlg, text="Оплата общежития", font=(FONT, 13, "bold"),
                 bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(14, 8), padx=20)
        for lbl, var, vals in [("Месяц", month_var, MONTHS), ("Сумма, ₸", amt_var, None)]:
            row = tk.Frame(dlg, bg=COLORS["frame"])
            row.pack(fill="x", padx=20, pady=4)
            tk.Label(row, text=lbl, width=12, anchor="w", font=(FONT, 10),
                     bg=COLORS["frame"], fg=COLORS["text"]).pack(side="left")
            if vals:
                ttk.Combobox(row, textvariable=var, values=vals, state="readonly", width=22).pack(side="left")
            else:
                tk.Entry(row, textvariable=var, width=24).pack(side="left")

        def confirm() -> None:
            try:
                amount = float(amt_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму.")
                return
            new_id = max(r["id"] for r in FINANCE_RECORDS) + 1
            FINANCE_RECORDS.append({
                "id": new_id, "student_id": sid, "op_type": "dorm",
                "amount": amount, "period": month_var.get(), "date": "2026-04-23",
                "status": "Оплачено", "sign": -1, "comment": f"Общежитие {month_var.get()} (симуляция)",
            })
            messagebox.showinfo("Оплата", f"Оплата за общежитие {month_var.get()} — {amount:,.0f} ₸ проведена.")
            dlg.destroy()
            self.render()

        tk.Button(dlg, text="Подтвердить", command=confirm,
                  bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=8).pack(pady=14)

    # ─────────────────────────────────────────────
    # БУХГАЛТЕР / АДМИНИСТРАТОР — панель управления
    # ─────────────────────────────────────────────
    def _render_staff(self) -> None:
        nb = ttk.Notebook(self.host_frame)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        # ── Вкладка «Все операции» ──
        tab_all = tk.Frame(nb, bg=COLORS["frame"])
        nb.add(tab_all, text="📋 Все операции")
        self._build_all_ops_tab(tab_all)

        # ── Вкладка «Начисление» ──
        tab_add = tk.Frame(nb, bg=COLORS["frame"])
        nb.add(tab_add, text="➕ Начислить / списать")
        self._build_charge_tab(tab_add)

        # ── Вкладка «Должники» ──
        tab_debt = tk.Frame(nb, bg=COLORS["frame"])
        nb.add(tab_debt, text="⚠ Должники")
        self._build_debtors_tab(tab_debt)

        # ── Вкладка «Стипендии и соцвыплаты» ──
        tab_sch = tk.Frame(nb, bg=COLORS["frame"])
        nb.add(tab_sch, text="🎓 Стипендии / соцвыплаты")
        self._build_scholarships_tab(tab_sch)

    def _build_all_ops_tab(self, parent: tk.Frame) -> None:
        cols   = ("date", "student", "op_type", "amount", "period", "status", "comment")
        heads  = {"date":"Дата", "student":"Студент", "op_type":"Тип", "amount":"Сумма, ₸",
                  "period":"Период", "status":"Статус", "comment":"Комментарий"}
        widths = {"date":100, "student":200, "op_type":170, "amount":110, "period":100, "status":110, "comment":230}

        tree = ttk.Treeview(parent, columns=cols, show="headings", height=24)
        for key, title in heads.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="e" if key == "amount" else "w")
        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=8, pady=8)

        for r in sorted(FINANCE_RECORDS, key=lambda x: x["date"], reverse=True):
            sign = "+" if r["sign"] == 1 else "–"
            tree.insert("", "end", values=(
                r["date"], _student_name(r["student_id"]),
                FINANCE_TYPES.get(r["op_type"], r["op_type"]),
                f"{sign}{r['amount']:,.0f}", r["period"], r["status"], r["comment"],
            ))

    def _build_charge_tab(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Форма начисления / списания",
                 font=(FONT, 13, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(14, 10))

        form = tk.Frame(parent, bg=COLORS["frame"])
        form.pack(padx=30)

        student_names = [s["full_name"] for s in sorted(STUDENTS, key=lambda s: s["full_name"])]
        stud_var   = tk.StringVar(value=student_names[0] if student_names else "")
        type_var   = tk.StringVar(value=list(FINANCE_TYPES.keys())[0])
        amount_var = tk.StringVar(value="5000")
        period_var = tk.StringVar(value=SEMESTERS[-1])
        sign_var   = tk.StringVar(value="начисление")
        comment_var = tk.StringVar(value="")

        rows = [
            ("Студент",        stud_var,    "combo", student_names),
            ("Тип операции",   type_var,    "combo", list(FINANCE_TYPES.keys())),
            ("Знак",           sign_var,    "combo", ["начисление", "списание"]),
            ("Сумма, ₸",       amount_var,  "entry", None),
            ("Период",         period_var,  "combo", SEMESTERS + MONTHS),
            ("Комментарий",    comment_var, "entry", None),
        ]
        for idx, (lbl, var, ftype, vals) in enumerate(rows):
            tk.Label(form, text=lbl, font=(FONT, 10), bg=COLORS["frame"], fg=COLORS["text"],
                     anchor="w", width=16).grid(row=idx, column=0, sticky="w", pady=7)
            if ftype == "combo":
                ttk.Combobox(form, textvariable=var, values=vals, state="readonly", width=34).grid(row=idx, column=1, pady=7, padx=8)
            else:
                tk.Entry(form, textvariable=var, width=36).grid(row=idx, column=1, pady=7, padx=8)

        def charge() -> None:
            try:
                amount = float(amount_var.get().replace(",", "").strip())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму.")
                return
            sid = next((s["id"] for s in STUDENTS if s["full_name"] == stud_var.get()), None)
            if sid is None:
                messagebox.showerror("Ошибка", "Студент не найден.")
                return
            sign = 1 if sign_var.get() == "начисление" else -1
            new_id = max(r["id"] for r in FINANCE_RECORDS) + 1 if FINANCE_RECORDS else 1
            FINANCE_RECORDS.append({
                "id": new_id, "student_id": sid,
                "op_type": type_var.get(), "amount": amount,
                "period": period_var.get(), "date": "2026-04-23",
                "status": "Выплачено" if sign == 1 else "Оплачено",
                "sign": sign,
                "comment": comment_var.get().strip() or FINANCE_TYPES.get(type_var.get(), ""),
            })
            messagebox.showinfo("Готово", f"Операция на {amount:,.0f} ₸ проведена для {stud_var.get()}.")
            self.render()

        tk.Button(form, text="Провести операцию", command=charge,
                  bg=COLORS["accent"], fg=COLORS["bg"], relief="flat", padx=14, pady=8,
                  ).grid(row=len(rows), column=0, columnspan=2, pady=16)

    def _build_debtors_tab(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Студенты с неоплаченными начислениями",
                 font=(FONT, 13, "bold"), bg=COLORS["frame"], fg=COLORS["error"]).pack(pady=(14, 8))

        cols   = ("student", "group", "op_type", "amount", "period", "date")
        heads  = {"student":"Студент", "group":"Группа", "op_type":"Тип", "amount":"Сумма, ₸", "period":"Период", "date":"Дата"}
        widths = {"student":220, "group":100, "op_type":180, "amount":110, "period":110, "date":100}

        frame = tk.Frame(parent, bg=COLORS["frame"])
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tree = ttk.Treeview(frame, columns=cols, show="headings", height=22)
        for key, title in heads.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="e" if key == "amount" else "w")
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        debtors = [r for r in FINANCE_RECORDS if r["sign"] == -1 and r["status"] == "Не оплачено"]
        for r in debtors:
            s = next((st for st in STUDENTS if st["id"] == r["student_id"]), None)
            tree.insert("", "end", values=(
                _student_name(r["student_id"]),
                s["group"] if s else "—",
                FINANCE_TYPES.get(r["op_type"], r["op_type"]),
                f"{r['amount']:,.0f}",
                r["period"], r["date"],
            ))

        if not debtors:
            tk.Label(parent, text="Должников нет 🎉",
                     font=(FONT, 13), bg=COLORS["frame"], fg=COLORS["success"]).pack(pady=30)

    def _build_scholarships_tab(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Стипендии и социальные выплаты",
                 font=(FONT, 13, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(14, 8))

        cols   = ("date", "student", "op_type", "amount", "period", "status")
        heads  = {"date":"Дата", "student":"Студент", "op_type":"Тип", "amount":"Сумма, ₸", "period":"Период", "status":"Статус"}
        widths = {"date":100, "student":210, "op_type":200, "amount":110, "period":110, "status":110}

        frame = tk.Frame(parent, bg=COLORS["frame"])
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tree = ttk.Treeview(frame, columns=cols, show="headings", height=22)
        for key, title in heads.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="e" if key == "amount" else "w")
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        sch_types = {"scholarship_base", "scholarship_high", "social"}
        records = sorted(
            [r for r in FINANCE_RECORDS if r["op_type"] in sch_types],
            key=lambda r: r["date"], reverse=True,
        )
        total = sum(r["amount"] for r in records)
        for r in records:
            tree.insert("", "end", values=(
                r["date"], _student_name(r["student_id"]),
                FINANCE_TYPES.get(r["op_type"], r["op_type"]),
                f"+{r['amount']:,.0f}", r["period"], r["status"],
            ))

        tk.Label(parent, text=f"Итого выплачено по стипендиям и соцвыплатам: {total:,.0f} ₸",
                 font=(FONT, 11, "bold"), bg=COLORS["frame"], fg=COLORS["success"]).pack(pady=(6, 10))

    def _clear(self) -> None:
        for w in self.host_frame.winfo_children():
            w.destroy()

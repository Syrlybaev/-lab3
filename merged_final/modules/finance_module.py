from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from data_sample import USERS
from services.auth import SessionUser
from ui.theme import COLORS, FONT


class FinanceModule:
    def __init__(self, host_frame: tk.Frame, current_user: SessionUser) -> None:
        self.host_frame = host_frame
        self.current_user = current_user

    def render_salary(self) -> None:
        self._clear()
        tk.Label(self.host_frame, text="ЗАРПЛАТНАЯ ВЕДОМОСТЬ", font=(FONT, 18, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=20)
        info = tk.Frame(self.host_frame, bg=COLORS["bg"])
        info.pack(padx=30, pady=30, fill="x")
        amount = self.current_user.salary or 0
        rows = [
            ("Сотрудник", self.current_user.full_name),
            ("Роли", ", ".join(self.current_user.roles)),
            ("Способ входа", "Пароль" if self.current_user.auth_method == "password" else "Токен"),
            ("Сумма", f"{amount} руб."),
        ]
        for title, value in rows:
            line = tk.Frame(info, bg=COLORS["bg"])
            line.pack(fill="x", pady=8)
            tk.Label(line, text=f"{title}:", width=18, anchor="w", font=(FONT, 11, "bold"), bg=COLORS["bg"], fg=COLORS["subtext"]).pack(side="left")
            tk.Label(line, text=value, anchor="w", font=(FONT, 11), bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")

    def render_finance_overview(self) -> None:
        self._clear()
        tk.Label(self.host_frame, text="ФИНАНСЫ И ВЫПЛАТЫ", font=(FONT, 18, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=10)
        columns = ("login", "full_name", "salary")
        tree = ttk.Treeview(self.host_frame, columns=columns, show="headings", height=15)
        tree.heading("login", text="Логин")
        tree.heading("full_name", text="ФИО")
        tree.heading("salary", text="Зарплата")
        tree.column("login", width=120, anchor="w")
        tree.column("full_name", width=280, anchor="w")
        tree.column("salary", width=160, anchor="center")
        for login, data in USERS.items():
            if data.get("salary") is None:
                continue
            tree.insert("", "end", values=(login, data["full_name"], f"{data['salary']} руб."))
        tree.pack(fill="both", expand=True, padx=12, pady=12)

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

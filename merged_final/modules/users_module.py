from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from data_sample import ROLE_LABELS, USERS
from ui.theme import COLORS, FONT


class UsersModule:
    def __init__(self, host_frame: tk.Frame) -> None:
        self.host_frame = host_frame

    def render(self) -> None:
        self._clear()
        tk.Label(self.host_frame, text="ПОЛЬЗОВАТЕЛИ СИСТЕМЫ", font=(FONT, 18, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=10)
        columns = ("login", "full_name", "roles", "context")
        tree = ttk.Treeview(self.host_frame, columns=columns, show="headings", height=15)
        tree.heading("login", text="Логин")
        tree.heading("full_name", text="ФИО")
        tree.heading("roles", text="Роль")
        tree.heading("context", text="Контекст")
        tree.column("login", width=130, anchor="w")
        tree.column("full_name", width=260, anchor="w")
        tree.column("roles", width=220, anchor="w")
        tree.column("context", width=200, anchor="w")
        for login, data in USERS.items():
            context = data.get("group") or (", ".join(str(x) for x in data.get("departments", [])) or "—")
            title = ", ".join(ROLE_LABELS.get(role, role) for role in data["roles"])
            tree.insert("", "end", values=(login, data["full_name"], title, context))
        tree.pack(fill="both", expand=True, padx=12, pady=12)

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

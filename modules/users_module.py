from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from data_sample import ROLE_LABELS, USERS, hash_password
from ui.theme import COLORS, FONT


class UsersModule:
    def __init__(self, host_frame: tk.Frame) -> None:
        self.host_frame = host_frame
        self.tree: ttk.Treeview | None = None

    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(15, 6))
        tk.Label(
            self.host_frame,
            text="Администратор управляет учетными записями и паролями на базе постоянных многократно используемых паролей.",
            font=(FONT, 11),
            bg=COLORS["frame"],
            fg=COLORS["subtext"],
            wraplength=900,
        ).pack(pady=(0, 10))

        toolbar = tk.Frame(self.host_frame, bg=COLORS["frame"])
        toolbar.pack(fill="x", padx=12, pady=(0, 8))
        tk.Button(
            toolbar,
            text="Сбросить пароль",
            font=(FONT, 10, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["bg"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._reset_password,
        ).pack(side="right")
        tk.Button(
            toolbar,
            text="Активировать / блокировать",
            font=(FONT, 10),
            bg=COLORS["button"],
            fg=COLORS["text"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._toggle_user_status,
        ).pack(side="right", padx=(0, 8))

        columns = ("login", "full_name", "role", "is_active", "last_password_change")
        tree = ttk.Treeview(self.host_frame, columns=columns, show="headings", height=18)
        headings = {
            "login": "Логин",
            "full_name": "ФИО",
            "role": "Роль",
            "is_active": "Статус",
            "last_password_change": "Смена пароля",
        }
        widths = {
            "login": 140,
            "full_name": 280,
            "role": 160,
            "is_active": 120,
            "last_password_change": 130,
        }
        for key, title in headings.items():
            tree.heading(key, text=title)
            tree.column(key, width=widths[key], anchor="w")

        for login, user in USERS.items():
            tree.insert(
                "",
                "end",
                iid=login,
                values=(
                    login,
                    user["full_name"],
                    ROLE_LABELS.get(user["role"], user["role"]),
                    "Активен" if user["is_active"] else "Заблокирован",
                    user["last_password_change"],
                ),
            )
        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.tree = tree

    def _selected_login(self) -> str | None:
        if not self.tree:
            return None
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Пользователи", "Сначала выберите учетную запись.")
            return None
        return selected[0]

    def _toggle_user_status(self) -> None:
        login = self._selected_login()
        if login is None:
            return
        USERS[login]["is_active"] = not USERS[login]["is_active"]
        self.render()

    def _reset_password(self) -> None:
        login = self._selected_login()
        if login is None:
            return
        USERS[login]["password_hash"] = hash_password("welcome2026")
        USERS[login]["last_password_change"] = "2026-04-23"
        messagebox.showinfo(
            "Пользователи",
            f"Пароль пользователя {login} сброшен на demo-значение: welcome2026",
        )
        self.render()

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

from __future__ import annotations

import tkinter as tk

from data_sample import SCHEDULE_DATA
from ui.theme import COLORS, FONT


class ScheduleModule:
    def __init__(self, host_frame: tk.Frame) -> None:
        self.host_frame = host_frame

    def render(self) -> None:
        self._clear()
        tk.Label(
            self.host_frame,
            text="РАСПИСАНИЕ ЗАНЯТИЙ",
            font=(FONT, 18, "bold"),
            bg=COLORS["frame"],
            fg=COLORS["accent"],
        ).pack(pady=(10, 5))

        container = tk.Frame(self.host_frame, bg=COLORS["frame"])
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=COLORS["frame"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["frame"])
        scrollable_frame.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        headers = ["Пара", "Время", "Период", "Дисциплина", "Ауд.", "Преподаватель", "Тип", "Формат"]

        for day in days:
            day_schedule = [item for item in SCHEDULE_DATA if item["day"] == day]
            if not day_schedule:
                continue
            day_frame = tk.LabelFrame(
                scrollable_frame,
                text=day,
                font=(FONT, 13, "bold"),
                bg=COLORS["frame"],
                fg=COLORS["accent"],
                bd=2,
                relief="groove",
            )
            day_frame.pack(fill="x", pady=12, padx=12)
            rows = []
            for item in sorted(day_schedule, key=lambda x: x["pair"]):
                fmt = "● Очно" if item["format"] == "Очно" else "○ Дистант"
                rows.append([
                    str(item["pair"]),
                    item["time"],
                    f"{item['period_start']}-{item['period_end']}",
                    item["subject"],
                    item["room"],
                    item["teacher"],
                    item["type"],
                    fmt,
                ])
            self._create_table(day_frame, headers, rows)

    def render_stub(self, title: str, text: str) -> None:
        self._clear()
        tk.Label(self.host_frame, text=title, font=(FONT, 18, "bold"), bg=COLORS["frame"], fg=COLORS["accent"]).pack(pady=(30, 20))
        tk.Label(self.host_frame, text=text, font=(FONT, 12), bg=COLORS["frame"], fg=COLORS["text"]).pack()

    def _create_table(self, parent: tk.Widget, headers: list[str], rows: list[list[str]]) -> None:
        header_frame = tk.Frame(parent, bg=COLORS["button"])
        header_frame.pack(fill="x", pady=(0, 2))
        col_widths = [50, 100, 100, 180, 70, 180, 110, 90]

        for idx, (header, width) in enumerate(zip(headers, col_widths)):
            tk.Label(
                header_frame,
                text=header,
                font=(FONT, 9, "bold"),
                bg=COLORS["button"],
                fg=COLORS["text"],
                width=width // 7,
                anchor="center",
                padx=4,
                pady=4,
            ).grid(row=0, column=idx, sticky="nsew")
            header_frame.grid_columnconfigure(idx, weight=1)

        for row_data in rows:
            is_online = row_data[7] == "● Очно"
            row_bg = COLORS["online_bg"] if is_online else COLORS["offline_bg"]
            text_color = COLORS["online_text"] if is_online else COLORS["offline_text"]
            row_frame = tk.Frame(parent, bg=row_bg)
            row_frame.pack(fill="x", pady=1)
            for idx, (val, width) in enumerate(zip(row_data, col_widths)):
                tk.Label(
                    row_frame,
                    text=val,
                    font=(FONT, 9),
                    bg=row_bg,
                    fg=text_color,
                    width=width // 7,
                    anchor="center",
                    padx=4,
                    pady=4,
                ).grid(row=0, column=idx, sticky="nsew")
                row_frame.grid_columnconfigure(idx, weight=1)

    def _clear(self) -> None:
        for widget in self.host_frame.winfo_children():
            widget.destroy()

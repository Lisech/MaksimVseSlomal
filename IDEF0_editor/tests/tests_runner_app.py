"""
tests_runner_app.py — отдельное приложение-раннер тестов.

Задача:
- открыть отдельное окно;
- предоставить РУЧНЫЕ тесты с подтверждением выполнения (чек-лист);
- сохранять отчёт о прогоне (PASS/FAIL) рядом с tests_runner.exe.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


def _base_dir() -> str:
    # В frozen режиме sys.executable указывает на tests_runner.exe
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def _default_reports_dir() -> str:
    d = os.path.join(_base_dir(), "test_reports")
    os.makedirs(d, exist_ok=True)
    return d


def _list_reports() -> list[str]:
    """Возвращает список путей к отчётам (новые сверху)."""
    reports_dir = _default_reports_dir()
    out: list[str] = []
    try:
        for name in os.listdir(reports_dir):
            if name.lower().endswith(".json") and name.startswith("manual_test_report_"):
                out.append(os.path.join(reports_dir, name))
    except Exception:
        return []
    out.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return out


MANUAL_CHECKLIST = [
    ("Подготовка", [
        "Приложение запускается без ошибок/крашей.",
        "Окно отображается корректно (панели, холст, иконки).",
        "Курсор/фокус: клики по холсту дают фокус холсту (горячие клавиши работают).",
    ]),
    ("Файлы", [
        "Новый: холст очищен, сетка видна, выделение сброшено.",
        "Сохранить как: создаётся .json, сообщение об успехе.",
        "Сохранить: изменения сохраняются в тот же файл.",
        "Открыть: блоки/стрелки восстановлены; блоки выделяются кликом; режим = выбор.",
    ]),
    ("Блоки", [
        "Создание блока (drag&drop) работает, блок появляется и выделяется.",
        "Выделение блока кликом по прямоугольнику и по тексту работает.",
        "Перемещение блока обновляет стрелки и свойства.",
        "Resize блока обновляет текст/стрелки.",
        "Свойства блока (текст/цвет/толщина/X/Y/размер) применяются корректно.",
        "Копирование/удаление блока кнопками работает без артефактов.",
    ]),
    ("Стрелки", [
        "Создание стрелки (все варианты: блок-блок, блок-точка, точка-блок, точка-точка) работает.",
        "Выделение стрелки кликом по линии/хитбоксу/наконечнику работает.",
        "Перетаскивание концов стрелки: показ точек прикрепления; attach при отпускании рядом.",
        "Прикрепление: авто-колена не сбрасываются; конец стрелки смотрит в блок и вплотную к границе.",
        "Разморозка маршрута кнопкой возвращает авто-роутинг.",
        "Создать точку сгиба: кнопка → клик по холсту → появляется ручка; до кнопки третья точка не появляется.",
        "Отступ от блоков: трасса не лежит на краю блока, есть зазор.",
    ]),
    ("Слои/уровни", [
        "Панель слоёв открывается/закрывается, дерево отображается.",
        "Переход по дереву (double click) работает: уровень меняется, блок выделяется, режим = выбор.",
    ]),
    ("Undo/Redo", [
        "Undo/Redo корректно откатывает/возвращает 5–10 действий; интерактивность не пропадает.",
    ]),
    ("Горячие клавиши", [
        "Ctrl+C / Ctrl+V / Ctrl+X работают для блока и стрелки; без крашей.",
    ]),
    ("Масштаб/пан", [
        "Ctrl+колесо масштабирует; пробел+drag панорамирует; отпускание возвращает выбор.",
    ]),
    ("Тема", [
        "Переключение темы работает; стрелки/ручки/точки прикрепления контрастны.",
    ]),
]


class TestsRunnerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("IDEF0 Editor — Manual Tests")
        self.geometry("980x720")
        self.minsize(820, 560)

        self.loaded_report_path: str | None = None
        self.loaded_report_status: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = ttk.Frame(container)
        header.pack(fill="x")

        self.status_var = tk.StringVar(value="Готов к ручному прогону")
        ttk.Label(header, textvariable=self.status_var).pack(side="left")

        btns = ttk.Frame(header)
        btns.pack(side="right")
        ttk.Button(btns, text="Открыть отчёт", command=self.open_report).pack(side="right")
        ttk.Button(btns, text="Сбросить", command=self.reset_all).pack(side="right")
        ttk.Button(btns, text="Сохранить отчёт", command=self.save_report).pack(side="right", padx=(0, 8))

        history = ttk.Labelframe(container, text="Прошлые отчёты")
        history.pack(fill="x", pady=(12, 0))
        self.report_paths = _list_reports()
        self.report_choice = tk.StringVar(value=self.report_paths[0] if self.report_paths else "")
        self.report_combo = ttk.Combobox(
            history,
            textvariable=self.report_choice,
            values=self.report_paths,
            state="readonly" if self.report_paths else "disabled",
        )
        self.report_combo.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        ttk.Button(history, text="Загрузить выбранный", command=self.load_selected_report).pack(side="left", padx=(0, 8), pady=8)

        meta = ttk.Labelframe(container, text="Метаданные прогона")
        meta.pack(fill="x", pady=(12, 12))

        self.meta_tester = tk.StringVar(value="")
        self.meta_version = tk.StringVar(value="")
        self.meta_date = tk.StringVar(value=_dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.meta_loaded = tk.StringVar(value="")

        ttk.Label(meta, text="Тестер").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(meta, textvariable=self.meta_tester).grid(row=0, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(meta, text="Версия/коммит").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(meta, textvariable=self.meta_version).grid(row=0, column=3, sticky="ew", padx=8, pady=6)
        ttk.Label(meta, text="Дата").grid(row=0, column=4, sticky="w", padx=8, pady=6)
        ttk.Entry(meta, textvariable=self.meta_date).grid(row=0, column=5, sticky="ew", padx=8, pady=6)
        ttk.Label(meta, textvariable=self.meta_loaded).grid(row=1, column=0, columnspan=6, sticky="w", padx=8, pady=(0, 8))
        meta.columnconfigure(1, weight=1)
        meta.columnconfigure(3, weight=1)
        meta.columnconfigure(5, weight=1)

        body = ttk.Frame(container)
        body.pack(fill="both", expand=True)

        # Scrollable checklist
        canvas = tk.Canvas(body, highlightthickness=0)
        vsb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._checklist_frame = ttk.Frame(canvas)
        self._checklist_window = canvas.create_window((0, 0), window=self._checklist_frame, anchor="nw")

        def _on_frame_config(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_config(e):
            canvas.itemconfigure(self._checklist_window, width=e.width)

        self._checklist_frame.bind("<Configure>", _on_frame_config)
        canvas.bind("<Configure>", _on_canvas_config)

        self._vars: list[tuple[str, str, tk.BooleanVar]] = []  # (section, text, var)
        self._build_checklist_widgets()

        notes = ttk.Labelframe(container, text="Заметки/дефекты (опционально)")
        notes.pack(fill="both", expand=False, pady=(12, 0))
        self.notes_text = tk.Text(notes, height=6)
        self.notes_text.pack(fill="both", expand=True, padx=8, pady=8)
    
    def _refresh_reports_list(self) -> None:
        self.report_paths = _list_reports()
        if not self.report_paths:
            self.report_combo.configure(values=[], state="disabled")
            self.report_choice.set("")
            return
        self.report_combo.configure(values=self.report_paths, state="readonly")
        if self.report_choice.get() not in self.report_paths:
            self.report_choice.set(self.report_paths[0])

    def _build_checklist_widgets(self) -> None:
        for sect_title, items in MANUAL_CHECKLIST:
            sect = ttk.Labelframe(self._checklist_frame, text=sect_title)
            sect.pack(fill="x", padx=6, pady=6)
            for it in items:
                v = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(sect, text=it, variable=v, command=self._update_progress)
                cb.pack(anchor="w", padx=10, pady=2)
                self._vars.append((sect_title, it, v))
        self._update_progress()

    def _update_progress(self) -> None:
        total = len(self._vars)
        done = sum(1 for _s, _t, v in self._vars if v.get())
        self.status_var.set(f"Выполнено: {done}/{total}. PASS доступен только если всё отмечено и вы сохраните отчёт.")

    def reset_all(self) -> None:
        for _s, _t, v in self._vars:
            v.set(False)
        self.notes_text.delete("1.0", "end")
        self.loaded_report_path = None
        self.loaded_report_status = None
        self.meta_loaded.set("")
        self._update_progress()

    def _compute_status(self) -> str:
        if all(v.get() for _s, _t, v in self._vars):
            return "PASS"
        return "FAIL"

    def save_report(self) -> None:
        """
        Сохраняет JSON-отчёт с подтверждением выполнения.
        PASS возможен только если отмечены все пункты.
        """
        status = self._compute_status()

        report = {
            "type": "manual_test_report",
            "status": status,
            "created_at": _dt.datetime.now().isoformat(timespec="seconds"),
            "meta": {
                "tester": self.meta_tester.get().strip(),
                "version": self.meta_version.get().strip(),
                "date": self.meta_date.get().strip(),
                "os": os.name,
            },
            "items": [
                {"section": s, "text": t, "done": bool(v.get())}
                for s, t, v in self._vars
            ],
            "notes": self.notes_text.get("1.0", "end").strip(),
        }

        reports_dir = _default_reports_dir()
        ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(reports_dir, f"manual_test_report_{ts}.json")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчёт:\n{e}")
            return

        self.status_var.set(f"Отчёт сохранён: {out_path} (status={status})")
        messagebox.showinfo("Отчёт сохранён", f"Статус: {status}\nФайл:\n{out_path}")
        self._refresh_reports_list()

    def open_report(self) -> None:
        """Открыть отчёт через диалог выбора файла."""
        reports_dir = _default_reports_dir()
        path = filedialog.askopenfilename(
            initialdir=reports_dir,
            filetypes=[("JSON reports", "*.json"), ("All files", "*.*")],
            title="Открыть тест-репорт",
        )
        if path:
            self.load_report(path)

    def load_selected_report(self) -> None:
        path = self.report_choice.get().strip()
        if not path:
            return
        self.load_report(path)

    def load_report(self, path: str) -> None:
        """Загружает прошлый тест-репорт в интерфейс."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                report = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать отчёт:\n{e}")
            return
        
        if not isinstance(report, dict) or report.get("type") != "manual_test_report":
            messagebox.showerror("Ошибка", "Файл не похож на manual_test_report (неверный формат).")
            return
        
        meta = report.get("meta") or {}
        try:
            self.meta_tester.set(str(meta.get("tester", "")))
            self.meta_version.set(str(meta.get("version", "")))
            self.meta_date.set(str(meta.get("date", "")) or self.meta_date.get())
        except Exception:
            pass
        
        # Заполняем чек-лист по совпадению (section,text)
        wanted: dict[tuple[str, str], bool] = {}
        for it in report.get("items") or []:
            try:
                key = (str(it.get("section", "")), str(it.get("text", "")))
                wanted[key] = bool(it.get("done", False))
            except Exception:
                continue
        for s, t, v in self._vars:
            v.set(wanted.get((s, t), False))
        
        self.notes_text.delete("1.0", "end")
        notes = report.get("notes", "")
        if notes:
            self.notes_text.insert("1.0", str(notes))
        
        self.loaded_report_path = path
        self.loaded_report_status = str(report.get("status", ""))
        created_at = str(report.get("created_at", ""))
        base_name = os.path.basename(path)
        self.meta_loaded.set(f"Загружен отчёт: {base_name} (created_at={created_at}, status={self.loaded_report_status})")
        self._update_progress()


def main() -> int:
    app = TestsRunnerApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



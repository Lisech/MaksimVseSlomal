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


# Словарь с описаниями тестов (ключ - текст теста, значение - описание)
TEST_DESCRIPTIONS = {
    "Приложение запускается без ошибок/крашей.": 
        "Тест 1: Запуск приложения\n\n"
        "Цель: Проверка базовой работоспособности приложения\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Приложение запускается без ошибок, исключений или крашей\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Приложение не запускается, выдает ошибку, крашится при старте\n\n"
        "Инструкция: Запустить приложение и проверить отсутствие ошибок в консоли/логах",
    
    "Окно отображается корректно (панели, холст, иконки).":
        "Тест 2: Отображение интерфейса\n\n"
        "Цель: Проверка корректности отображения всех элементов интерфейса\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Все панели видны, холст отображается, иконки загружены и видны\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Панели не видны, холст пустой/не отображается, иконки отсутствуют или битые\n\n"
        "Инструкция: Визуально проверить наличие всех элементов интерфейса",
    
    "Курсор/фокус: клики по холсту дают фокус холсту (горячие клавиши работают).":
        "Тест 3: Фокус и горячие клавиши\n\n"
        "Цель: Проверка корректной работы фокуса и горячих клавиш\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Клик по холсту активирует фокус, горячие клавиши работают\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Фокус не переключается на холст, горячие клавиши не работают\n\n"
        "Инструкция: Кликнуть по холсту и проверить работу горячих клавиш (например, Ctrl+Z)",
    
    "Новый: холст очищен, сетка видна, выделение сброшено.":
        "Тест 4: Создание нового проекта\n\n"
        "Цель: Проверка функции создания нового проекта\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Холст очищен, сетка отображается, выделение сброшено, режим = выбор\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Холст не очищен, сетка не видна, осталось выделение, режим не сброшен\n\n"
        "Инструкция: Создать несколько элементов, затем выбрать 'Новый' и проверить состояние",
    
    "Сохранить как: создаётся .json, сообщение об успехе.":
        "Тест 5: Сохранение проекта (Сохранить как)\n\n"
        "Цель: Проверка функции сохранения проекта в новый файл\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Файл .json создается, появляется сообщение об успешном сохранении\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Файл не создается, ошибка при сохранении, нет сообщения об успехе\n\n"
        "Инструкция: Создать элементы, выбрать 'Сохранить как', указать имя файла, проверить создание",
    
    "Сохранить: изменения сохраняются в тот же файл.":
        "Тест 6: Сохранение проекта (Сохранить)\n\n"
        "Цель: Проверка функции сохранения изменений в существующий файл\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Изменения сохраняются в тот же файл, файл обновляется\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Изменения не сохраняются, файл не обновляется, ошибка сохранения\n\n"
        "Инструкция: Открыть файл, внести изменения, выбрать 'Сохранить', проверить файл",
    
    "Открыть: блоки/стрелки восстановлены; блоки выделяются кликом; режим = выбор.":
        "Тест 7: Открытие проекта\n\n"
        "Цель: Проверка функции загрузки проекта из файла\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Блоки и стрелки восстановлены, блоки выделяются кликом, режим = выбор\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Элементы не загружены, блоки не выделяются, режим неверный, ошибка загрузки\n\n"
        "Инструкция: Сохранить проект с элементами, закрыть приложение, открыть файл, проверить восстановление",
    
    "Создание блока (drag&drop) работает, блок появляется и выделяется.":
        "Тест 8: Создание блока\n\n"
        "Цель: Проверка функции создания блока через drag&drop\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Блок появляется на холсте, автоматически выделяется после создания\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Блок не создается, не появляется на холсте, не выделяется\n\n"
        "Инструкция: Перетащить блок из панели инструментов на холст, проверить появление и выделение",
    
    "Выделение блока кликом по прямоугольнику и по тексту работает.":
        "Тест 9: Выделение блока\n\n"
        "Цель: Проверка функции выделения блока различными способами\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Блок выделяется кликом по прямоугольнику и кликом по тексту\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Блок не выделяется, выделяется только по одной области\n\n"
        "Инструкция: Кликнуть по прямоугольнику блока, затем по тексту блока, проверить выделение",
    
    "Перемещение блока обновляет стрелки и свойства.":
        "Тест 10: Перемещение блока\n\n"
        "Цель: Проверка обновления связанных элементов при перемещении блока\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "При перемещении блока стрелки обновляются, свойства обновляются\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Стрелки не обновляются, остаются на старых позициях, свойства не обновляются\n\n"
        "Инструкция: Создать блок со стрелками, переместить блок, проверить обновление стрелок",
    
    "Resize блока обновляет текст/стрелки.":
        "Тест 11: Изменение размера блока (Resize)\n\n"
        "Цель: Проверка обновления элементов при изменении размера блока\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "При изменении размера текст и стрелки обновляются корректно\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Текст не обновляется, стрелки остаются на старых позициях\n\n"
        "Инструкция: Изменить размер блока, проверить обновление текста и стрелок",
    
    "Свойства блока (текст/цвет/толщина/X/Y/размер) применяются корректно.":
        "Тест 12: Свойства блока\n\n"
        "Цель: Проверка применения всех свойств блока через панель свойств\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Все свойства (текст, цвет, толщина, X, Y, размер) применяются и отображаются\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Свойства не применяются, не отображаются, значения не сохраняются\n\n"
        "Инструкция: Изменить каждое свойство блока в панели свойств, проверить применение",
    
    "Копирование/удаление блока кнопками работает без артефактов.":
        "Тест 13: Копирование и удаление блока\n\n"
        "Цель: Проверка функций копирования и удаления блока\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Копирование создает идентичный блок, удаление убирает блок без артефактов\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Копирование не работает, удаление оставляет артефакты, ошибки при операциях\n\n"
        "Инструкция: Скопировать блок, проверить создание копии, удалить блок, проверить отсутствие артефактов",
    
    "Создание стрелки (все варианты: блок-блок, блок-точка, точка-блок, точка-точка) работает.":
        "Тест 14: Создание стрелки (все варианты)\n\n"
        "Цель: Проверка создания стрелок во всех возможных конфигурациях\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Все варианты создания работают (блок-блок, блок-точка, точка-блок, точка-точка)\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Некоторые варианты не работают, стрелки не создаются, ошибки при создании\n\n"
        "Инструкция: Создать стрелки всех типов: от блока к блоку, от блока к точке, от точки к блоку, от точки к точке",
    
    "Выделение стрелки кликом по линии/хитбоксу/наконечнику работает.":
        "Тест 15: Выделение стрелки\n\n"
        "Цель: Проверка выделения стрелки различными способами\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Стрелка выделяется кликом по линии, хитбоксу и наконечнику\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Стрелка не выделяется, выделяется только по некоторым областям\n\n"
        "Инструкция: Кликнуть по линии стрелки, хитбоксу и наконечнику, проверить выделение",
    
    "Перетаскивание концов стрелки: показ точек прикрепления; attach при отпускании рядом.":
        "Тест 16: Перетаскивание концов стрелки\n\n"
        "Цель: Проверка функции изменения точек прикрепления стрелки\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "При перетаскивании показываются точки прикрепления, при отпускании рядом происходит прикрепление\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Точки прикрепления не показываются, прикрепление не происходит\n\n"
        "Инструкция: Перетащить конец стрелки к другому блоку, проверить показ точек и прикрепление",
    
    "Прикрепление: авто-колена не сбрасываются; конец стрелки смотрит в блок и вплотную к границе.":
        "Тест 17: Прикрепление стрелки к блоку\n\n"
        "Цель: Проверка корректности прикрепления стрелки к блоку\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Автоматические колена не сбрасываются, конец стрелки направлен в блок и вплотную к границе\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Колена сбрасываются, конец стрелки не направлен в блок, есть зазор от границы\n\n"
        "Инструкция: Прикрепить стрелку к блоку, проверить сохранение колен и правильное направление",
    
    "Разморозка маршрута кнопкой возвращает авто-роутинг.":
        "Тест 18: Разморозка маршрута\n\n"
        "Цель: Проверка функции разморозки заблокированного маршрута\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "При разморозке маршрут возвращается к автоматическому роутингу\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Маршрут не размораживается, авто-роутинг не включается\n\n"
        "Инструкция: Заблокировать маршрут, затем разморозить кнопкой, проверить возврат к авто-роутингу",
    
    "Создать точку сгиба: кнопка → клик по холсту → появляется ручка; до кнопки третья точка не появляется.":
        "Тест 19: Создание точки сгиба\n\n"
        "Цель: Проверка функции создания точки сгиба на стрелке\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "После нажатия кнопки и клика по холсту появляется ручка точки сгиба, до кнопки точка не появляется\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Точка сгиба не создается, появляется без нажатия кнопки, ручка не отображается\n\n"
        "Инструкция: Нажать кнопку создания точки сгиба, кликнуть по холсту, проверить появление ручки",
    
    "Отступ от блоков: трасса не лежит на краю блока, есть зазор.":
        "Тест 20: Отступ от блоков\n\n"
        "Цель: Проверка визуального отступа трассы стрелки от края блока\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Трасса стрелки не лежит на краю блока, есть визуальный зазор\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Трасса лежит на краю блока, нет зазора, стрелка визуально сливается с блоком\n\n"
        "Инструкция: Создать стрелку между блоками, проверить наличие отступа от границ блоков",
    
    "Панель слоёв открывается/закрывается, дерево отображается.":
        "Тест 21: Панель слоёв\n\n"
        "Цель: Проверка функциональности панели слоёв\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Панель открывается и закрывается, дерево иерархии отображается корректно\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Панель не открывается/не закрывается, дерево не отображается\n\n"
        "Инструкция: Открыть панель слоёв, проверить отображение дерева, закрыть панель",
    
    "Переход по дереву (double click) работает: уровень меняется, блок выделяется, режим = выбор.":
        "Тест 22: Переход по уровням\n\n"
        "Цель: Проверка навигации по иерархии уровней\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Двойной клик по элементу дерева меняет уровень, блок выделяется, режим = выбор\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Переход не происходит, блок не выделяется, режим не меняется\n\n"
        "Инструкция: Дважды кликнуть по блоку в дереве, проверить переход на уровень и выделение",
    
    "Undo/Redo корректно откатывает/возвращает 5–10 действий; интерактивность не пропадает.":
        "Тест 23: Откат и возврат действий\n\n"
        "Цель: Проверка системы отката и возврата действий\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Undo/Redo корректно откатывает/возвращает 5-10 действий, интерактивность сохраняется\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Откат не работает, возврат не работает, теряется интерактивность после отката\n\n"
        "Инструкция: Выполнить несколько действий, откатить их (Undo), затем вернуть (Redo), проверить состояние",
    
    "Ctrl+C / Ctrl+V / Ctrl+X работают для блока и стрелки; без крашей.":
        "Тест 24: Горячие клавиши копирования/вставки/вырезания\n\n"
        "Цель: Проверка работы стандартных горячих клавиш\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Ctrl+C/Ctrl+V/Ctrl+X работают для блоков и стрелок, нет крашей\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Горячие клавиши не работают, приложение крашится при использовании\n\n"
        "Инструкция: Выделить блок/стрелку, нажать Ctrl+C, затем Ctrl+V, проверить копирование; проверить Ctrl+X",
    
    "Ctrl+колесо масштабирует; пробел+drag панорамирует; отпускание возвращает выбор.":
        "Тест 25: Масштабирование и панорамирование\n\n"
        "Цель: Проверка функций масштабирования и панорамирования холста\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Ctrl+колесо масштабирует, пробел+drag панорамирует, отпускание возвращает режим выбора\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Масштабирование не работает, панорамирование не работает, режим не возвращается\n\n"
        "Инструкция: Нажать Ctrl и прокрутить колесо мыши, проверить масштаб; зажать пробел и перетащить, проверить пан",
    
    "Переключение темы работает; стрелки/ручки/точки прикрепления контрастны.":
        "Тест 26: Переключение темы\n\n"
        "Цель: Проверка функции переключения темы оформления\n\n"
        "УСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Переключение темы работает, стрелки/ручки/точки прикрепления контрастны и видны\n\n"
        "НЕУСПЕШНЫЙ СЦЕНАРИЙ:\n"
        "Тема не переключается, элементы не контрастны, плохая видимость\n\n"
        "Инструкция: Переключить тему, проверить видимость всех элементов (стрелки, ручки, точки прикрепления)",
}


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

    def _create_tooltip(self, widget, text):
        """Создает tooltip для виджета"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip, 
                text=text, 
                background="#ffffe0", 
                relief="solid", 
                borderwidth=1,
                font=("TkDefaultFont", 9),
                justify="left",
                wraplength=400
            )
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _build_checklist_widgets(self) -> None:
        for sect_title, items in MANUAL_CHECKLIST:
            sect = ttk.Labelframe(self._checklist_frame, text=sect_title)
            sect.pack(fill="x", padx=6, pady=6)
            for it in items:
                v = tk.BooleanVar(value=False)
                
                # Создаем фрейм для чекбокса и кнопки "Подробнее"
                item_frame = ttk.Frame(sect)
                item_frame.pack(fill="x", padx=10, pady=2)
                
                cb = ttk.Checkbutton(item_frame, text=it, variable=v, command=self._update_progress)
                cb.pack(side="left", anchor="w")
                
                # Получаем описание из словаря
                description = TEST_DESCRIPTIONS.get(it, "")
                
                # Добавляем кнопку "Подробнее" если есть описание
                if description:
                    # Сохраняем копии для замыкания
                    desc_copy = description.strip()
                    title_copy = it
                    
                    def show_details():
                        details_window = tk.Toplevel(self)
                        details_window.title(f"Описание теста: {title_copy[:50]}...")
                        details_window.geometry("600x400")
                        
                        text_widget = tk.Text(details_window, wrap="word", padx=10, pady=10)
                        text_widget.pack(fill="both", expand=True)
                        text_widget.insert("1.0", desc_copy)
                        text_widget.config(state="disabled")
                        
                        close_btn = ttk.Button(details_window, text="Закрыть", command=details_window.destroy)
                        close_btn.pack(pady=5)
                    
                    info_btn = ttk.Button(item_frame, text="ℹ Подробнее", width=12, command=show_details)
                    info_btn.pack(side="right", padx=(5, 0))
                    
                    # Также добавляем tooltip
                    tooltip_text = desc_copy[:200] + ("..." if len(desc_copy) > 200 else "")
                    self._create_tooltip(cb, tooltip_text)
                
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



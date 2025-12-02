"""
Чистый макет приложения - точная копия HTML макета
Все кнопки с заглушками
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import math
import sys
import json
from styles import Colors, Dimensions, Fonts
from properties import PropertiesPanel
from PIL import Image, ImageTk
from models import Block, Arrow, LayerManager

class IDEF0App:
    def __init__(self):
        self.root = tk.Tk()
        # Текущая тема приложения (False = светлая, True = тёмная)
        self.is_dark_theme = False
        # Убедимся, что при старте используются цвета светлой темы
        Colors.use_light()
        # Кэши и привязки для иконок
        self._icons = {}
        self._icon_bindings = []
        # Кнопки действий для выбранного блока (на холсте)
        self.block_action_buttons = []
        # Стеки для undo/redo (инициализируем до setup_ui)
        self.undo_stack = []  # стек для отмены действий
        self.redo_stack = []  # стек для повтора действий
        self.max_history_size = 50  # максимальный размер истории
        # Буфер обмена для копирования/вставки
        self.clipboard = None  # хранит скопированный элемент (блок или стрелка)
        self.clipboard_type = None  # "block" или "arrow"
        self.setup_window()
        # Инициализируем layer_manager до setup_ui, так как он используется в setup_main_layout
        self.layer_manager = LayerManager()  # Менеджер слоев для иерархии
        self.current_right_panel = "properties"  # или "layers"
        self.layers_panel_visible = False
        self.setup_ui()
        self.blocks = []
        self.arrows = []  # список стрелок
        self.next_block_id = 1
        self.next_arrow_id = 1  # счетчик для ID стрелок
        self.current_file_path = None  # путь к текущему файлу
        self.is_panning = False  # флаг режима панорамирования
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.selected_block = None  # текущий выбранный блок
        self.selected_arrow = None  # текущая выбранная стрелка
        self.dragging_block = None  # блок, который сейчас перетаскивается
        self.current_mode = "select"  # режим работы: "select" или "pan"
        self.drag_from_sidebar = False  # флаг перетаскивания из панели
        self.drag_preview = None  # превью перетаскиваемого блока
        self.resizing_block = None  # блок, который сейчас изменяется
        self.resize_handle_size = 12  # размер маркеров изменения размера (в 1.5 раза больше, чем было)
        self.resize_preview = None  # превью растягивания
        self.block_action_buttons = []
        self.arrow_action_buttons = []
        self.arrow_drag_handles = {}  # маркеры для перетаскивания концов стрелок
        self.dragging_arrow_end = None  # какой конец стрелки перетаскивается ("start" или "end")
        self.arrow_drawing_mode = False  # режим рисования стрелок
        self.arrow_start_block = None  # начальный блок для стрелки (если стрелка начинается от блока)
        self.arrow_start_x = None  # начальная координата X (если стрелка начинается не от блока)
        self.arrow_start_y = None  # начальная координата Y (если стрелка начинается не от блока)
        self.arrow_preview_line = None  # превью линии стрелки
        self.arrow_drawing = False  # флаг активного рисования стрелки
        self.zoom_scale = 1.0  # текущий масштаб
        self.attachment_points = []  # визуальные элементы точек прикрепления
        self.attachment_point_size = 12  # размер точки прикрепления
        self.attachment_snap_distance = 20  # расстояние для прикрепления
    
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("IDEF0 Editor — Макет")
        self.root.geometry("1200x700")
        self.root.configure(bg=Colors.BACKGROUND)
        self.root.minsize(1200, 800)
        
    
    def setup_ui(self):
        """Создание интерфейса - точная копия HTML макета"""
        # Header
        self.setup_header()

        # Main layout
        self.setup_main_layout()
        
        # Инициализируем состояние кнопок undo/redo
        self.update_undo_redo_buttons()

    def format_block_text(self, text, max_width, max_chars=None):
        """
        Форматирует текст блока с ограничением по символам и автопереносом до края блока.
        Текст автоматически переносится при достижении края блока (с учетом отступов).
        
        Args:
            text: Исходный текст
            max_width: Максимальная ширина блока в пикселях (для автопереноса)
            max_chars: Максимальное количество символов (если None, вычисляется автоматически)
        
        Returns:
            Текст с ограничением по символам (перенос выполняется автоматически через width)
        """
        if not text:
            return ""
        
        # Параметры шрифта для расчета
        font_size = 10
        padding = 10  # Отступы по 5px с каждой стороны
        
        # Вычисляем доступную ширину для текста
        available_width = max_width - padding
        
        # Если max_chars не указан, вычисляем его на основе ширины блока
        if max_chars is None:
            # Для шрифта Segoe UI 10pt средняя ширина символа примерно 6-7px
            # Используем более консервативную оценку 7px на символ для учета широких символов
            chars_per_line = max(1, int(available_width / 7))
            
            # Учитываем возможность многострочного текста
            # Высота строки примерно font_size * 1.4-1.5
            line_height = font_size * 1.5
            # Максимальная высота блока обычно позволяет 2-3 строки для стандартного блока
            # Но мы ограничимся разумным максимумом
            max_lines = max(1, min(5, int((max_width * 0.6) / line_height)))
            
            # Общее количество символов = символы на строку * количество строк
            max_chars = chars_per_line * max_lines
            
            # Ограничения: минимум 15 символов, максимум 80 (как в полях ввода)
            max_chars = max(15, min(80, max_chars))
        
        # Ограничение по символам с добавлением многоточия при обрезке
        if len(text) > max_chars:
            text = text[:max_chars - 3] + "..."  # Оставляем место для "..."
        
        # Возвращаем текст - tkinter Canvas автоматически выполнит перенос
        # при указании параметра width в create_text (width = available_width)
        # Перенос происходит до пересечения с краем блока благодаря параметру width
        return text

    def setup_hotkeys(self):
        """Привязывает горячие клавиши к действиям - работает всегда и во всех режимах"""
        
        def is_text_input_widget(widget):
            """Проверяет, является ли виджет полем ввода текста"""
            try:
                if widget is None:
                    return False
                widget_class = widget.winfo_class()
                # Проверяем класс виджета и тип
                if isinstance(widget, (tk.Entry, tk.Text)):
                    return True
                # Также проверяем по классу виджета (для ttk виджетов)
                if widget_class in ('Entry', 'Text', 'TEntry', 'TText'):
                    return True
                return False
            except:
                return False
        
        def safe_copy(e=None):
            """Безопасное копирование - работает всегда, кроме полей ввода"""
            try:
                widget = self.root.focus_get()
                if is_text_input_widget(widget):
                    return None  # Разрешаем стандартное поведение в полях ввода
            except:
                pass
            try:
                self.copy_selected()
            except Exception as ex:
                print(f"Ошибка при копировании: {ex}")
            return "break"  # Всегда блокируем дальнейшую обработку
        
        def safe_paste(e=None):
            """Безопасная вставка - работает всегда, кроме полей ввода"""
            try:
                widget = self.root.focus_get()
                if is_text_input_widget(widget):
                    return None  # Разрешаем стандартное поведение в полях ввода
            except:
                pass
            try:
                self.paste_clipboard()
            except Exception as ex:
                print(f"Ошибка при вставке: {ex}")
            return "break"  # Всегда блокируем дальнейшую обработку
        
        def safe_cut(e=None):
            """Безопасное вырезание - работает всегда, кроме полей ввода"""
            try:
                widget = self.root.focus_get()
                if is_text_input_widget(widget):
                    return None  # Разрешаем стандартное поведение в полях ввода
            except:
                pass
            try:
                self.cut_selected()
            except Exception as ex:
                print(f"Ошибка при вырезании: {ex}")
            return "break"  # Всегда блокируем дальнейшую обработку
        
        def safe_undo(e=None):
            """Безопасная отмена - работает всегда, кроме полей ввода"""
            try:
                widget = self.root.focus_get()
                if is_text_input_widget(widget):
                    return None  # Разрешаем стандартное поведение в полях ввода
            except:
                pass
            try:
                self.undo()
            except Exception as ex:
                print(f"Ошибка при отмене: {ex}")
            return "break"  # Всегда блокируем дальнейшую обработку
        
        def safe_redo(e=None):
            """Безопасный повтор - работает всегда, кроме полей ввода"""
            try:
                widget = self.root.focus_get()
                if is_text_input_widget(widget):
                    return None  # Разрешаем стандартное поведение в полях ввода
            except:
                pass
            try:
                self.redo()
            except Exception as ex:
                print(f"Ошибка при повторе: {ex}")
            return "break"  # Всегда блокируем дальнейшую обработку
        
        def safe_delete(e=None):
            """Безопасное удаление - работает всегда, кроме полей ввода"""
            try:
                widget = self.root.focus_get()
                if is_text_input_widget(widget):
                    return None  # Разрешаем стандартное поведение в полях ввода
            except:
                pass
            try:
                self.delete_selected()
            except Exception as ex:
                print(f"Ошибка при удалении: {ex}")
            return "break"  # Всегда блокируем дальнейшую обработку
        
        # Сохраняем ссылки на функции для использования в обработчиках
        self._hotkey_copy = safe_copy
        self._hotkey_paste = safe_paste
        self._hotkey_cut = safe_cut
        self._hotkey_undo = safe_undo
        self._hotkey_redo = safe_redo
        self._hotkey_delete = safe_delete
        
        # Универсальный обработчик для всех нажатий клавиш
        # Используем bind_all для глобальной привязки, которая работает везде
        def universal_key_handler(event):
            """Универсальный обработчик клавиш - работает всегда"""
            # Проверяем фокус, а не event.widget, так как bind_all может давать разные виджеты
            try:
                widget = self.root.focus_get()
                # Пропускаем события из полей ввода
                if is_text_input_widget(widget):
                    return
            except:
                pass
            
            # Обрабатываем комбинации с Control
            if event.state & 0x4:  # Control нажат
                key = event.keysym.lower()
                if key == 'c':
                    safe_copy(event)
                    return "break"
                elif key == 'v':
                    safe_paste(event)
                    return "break"
                elif key == 'x':
                    safe_cut(event)
                    return "break"
                elif key == 'z':
                    safe_undo(event)
                    return "break"
                elif key == 'y':
                    safe_redo(event)
                    return "break"
            # Обрабатываем Delete и BackSpace
            elif event.keysym in ('Delete', 'BackSpace'):
                safe_delete(event)
                return "break"
        
        # Привязываем горячие клавиши через bind_all для глобальной работы
        # bind_all работает на всех виджетах и всегда, независимо от фокуса
        # Используем add='+' для добавления обработчиков без замены существующих
        
        # Ctrl+C / Ctrl+Insert - Копирование
        self.root.bind_all("<Control-c>", safe_copy, add='+')
        self.root.bind_all("<Control-C>", safe_copy, add='+')
        self.root.bind_all("<Control-Insert>", safe_copy, add='+')
        
        # Ctrl+V / Shift+Insert - Вставка
        self.root.bind_all("<Control-v>", safe_paste, add='+')
        self.root.bind_all("<Control-V>", safe_paste, add='+')
        self.root.bind_all("<Shift-Insert>", safe_paste, add='+')
        
        # Ctrl+X - Вырезание
        self.root.bind_all("<Control-x>", safe_cut, add='+')
        self.root.bind_all("<Control-X>", safe_cut, add='+')
        
        # Ctrl+Z - Отмена
        self.root.bind_all("<Control-z>", safe_undo, add='+')
        self.root.bind_all("<Control-Z>", safe_undo, add='+')
        
        # Ctrl+Y / Ctrl+Shift+Z - Повтор
        self.root.bind_all("<Control-y>", safe_redo, add='+')
        self.root.bind_all("<Control-Y>", safe_redo, add='+')
        self.root.bind_all("<Control-Shift-z>", safe_redo, add='+')
        self.root.bind_all("<Control-Shift-Z>", safe_redo, add='+')
        
        # Delete / BackSpace - Удаление
        self.root.bind_all("<Delete>", safe_delete, add='+')
        self.root.bind_all("<BackSpace>", safe_delete, add='+')
        
        # Универсальный обработчик для всех клавиш (резервный)
        self.root.bind_all("<KeyPress>", universal_key_handler, add='+')
        
        # Привязываем к canvas для дополнительной надежности
        if hasattr(self, 'canvas'):
            self.canvas.bind("<Control-c>", safe_copy, add='+')
            self.canvas.bind("<Control-C>", safe_copy, add='+')
            self.canvas.bind("<Control-v>", safe_paste, add='+')
            self.canvas.bind("<Control-V>", safe_paste, add='+')
            self.canvas.bind("<Control-x>", safe_cut, add='+')
            self.canvas.bind("<Control-X>", safe_cut, add='+')
            self.canvas.bind("<Control-z>", safe_undo, add='+')
            self.canvas.bind("<Control-Z>", safe_undo, add='+')
            self.canvas.bind("<Control-y>", safe_redo, add='+')
            self.canvas.bind("<Control-Y>", safe_redo, add='+')
            self.canvas.bind("<Delete>", safe_delete, add='+')
            self.canvas.bind("<BackSpace>", safe_delete, add='+')
            self.canvas.bind("<KeyPress>", universal_key_handler, add='+')
            
            # Устанавливаем фокус на canvas при входе мыши и клике
            self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
            self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set(), add="+")
        
        # Устанавливаем фокус на root для начальной работы
        self.root.focus_set()
        
        # Устанавливаем возможность получения фокуса для всех виджетов
        def set_focus():
            if hasattr(self, 'canvas'):
                self.canvas.focus_set()
            else:
                self.root.focus_set()
        self.root.after(100, set_focus)
    
    def setup_header(self):
        """Верхняя панель как в HTML макете"""
        header_frame = tk.Frame(
            self.root,
            bg=Colors.SURFACE,
            height=46,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        # Сохраняем ссылку, чтобы обновлять цвета при смене темы
        self.header_frame = header_frame

        # Title
        title_label = tk.Label(
            header_frame,
            text="IDEF0 Editor",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY
        )
        title_label.pack(side=tk.LEFT, padx=(14, 6))

        # Toolbar buttons
        toolbar_frame = tk.Frame(header_frame, bg=Colors.SURFACE)
        toolbar_frame.pack(side=tk.LEFT, padx=12)
        self.toolbar_frame = toolbar_frame

        toolbar_buttons = [
            ("Новый", "FileText", (20,20)),
            ("Открыть", "FolderOpen", (20,20)),
            ("Сохранить", "Save", (20,20)),
            ("Сохранить как", "Download", (20,20)),
        ]

        for text, icon_name, size in toolbar_buttons:
            btn = self.create_toolbar_button(toolbar_frame, text)
            self.set_widget_icon(btn, icon_name, size, compound='left')
            btn.pack(side=tk.LEFT, padx=6)
            
            # Привязываем обработчики для кнопок файлов
            if text == "Новый":
                btn.configure(command=self.new_file)
            elif text == "Открыть":
                btn.configure(command=self.open_file)
            elif text == "Сохранить":
                btn.configure(command=self.save_file)
            elif text == "Сохранить как":
                btn.configure(command=self.save_file_as)

        # Spacer
        spacer = tk.Frame(header_frame, bg=Colors.SURFACE)
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Right controls
        right_frame = tk.Frame(header_frame, bg=Colors.SURFACE)
        right_frame.pack(side=tk.RIGHT, padx=14)
        self.right_frame = right_frame

        # Zoom controls
        zoom_frame = tk.Frame(right_frame, bg=Colors.SURFACE)
        zoom_frame.pack(side=tk.LEFT, padx=(0, 12))
        self.zoom_frame = zoom_frame
        
        # Zoom out button
        zoom_out_btn = tk.Button(
            zoom_frame,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        self.set_widget_icon(zoom_out_btn, "ZoomOut", (16,16))
        zoom_out_btn.configure(command=lambda: self.apply_zoom(0.9))
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(zoom_out_btn)
        
        # Zoom percentage
        self.zoom_label = tk.Label(zoom_frame, text="100%", bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY, font=("Segoe UI", 10))
        self.zoom_label.pack(side=tk.LEFT, padx=4)
        
        # Zoom in button
        zoom_in_btn = tk.Button(
            zoom_frame,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        self.set_widget_icon(zoom_in_btn, "ZoomIn", (16,16))
        zoom_in_btn.configure(command=lambda: self.apply_zoom(1.1))
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(zoom_in_btn)

        # Кнопка настроек
        settings_btn = self.create_toolbar_button(right_frame, "")
        self.set_widget_icon(settings_btn, "Settings", (20,20))
        settings_btn.configure(command=self.open_settings_menu)
        settings_btn.pack(side=tk.LEFT, padx=6)
        self.settings_btn = settings_btn

    def create_toolbar_button(self, parent, text):
        """Создает кнопку для тулбара в стиле HTML макета"""
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        self.apply_hover_effect(btn)
        return btn

    def setup_main_layout(self):
        """Основная layout-сетка как в HTML"""
        main_frame = tk.Frame(self.root, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        self.main_frame = main_frame

        # Configure grid layout
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Left sidebar
        self.setup_sidebar(main_frame)

        # Canvas area
        self.setup_canvas(main_frame)

        # Properties panel
        self.properties_panel = PropertiesPanel(main_frame, on_properties_change=self.on_properties_change)
        self.properties_panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))

        # Панель слоев (изначально скрыта)
        self.setup_layers_panel(main_frame)
        
        # Инициализируем footer с информацией об уровне (будет вызван после создания footer_right_label)

    def setup_sidebar(self, parent):
        """Левая панель инструментов"""
        sidebar_frame = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            width=54,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sidebar_frame.pack_propagate(False)
        self.sidebar_frame = sidebar_frame

        tools = [
            ("MousePointer2", "Выбрать"),
            ("Hand", "Перемещать"),
            ("Square", "Добавить блок"),
            ("ArrowRight", "Добавить стрелку"),
            ("Type", "Текст"),
            ("Layers", "Слои"),
            ("ChevronUp", "На передний план"),
            ("ChevronDown", "На задний план"),
            ("Trash2", "Удалить")
        ]

        for i, (icon_name, tooltip) in enumerate(tools):
            btn = tk.Button(
                sidebar_frame,
                text="",
                font=("Segoe UI", 12),
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=Colors.BORDER,
                activebackground=Colors.ACTIVE
            )
            self.set_widget_icon(btn, icon_name, (26, 26), compound='center')
            btn.configure(padx=16, pady=16)

            if icon_name == "MousePointer2":
                btn.configure(command=self.enable_select_mode)

            if icon_name == "Hand":
                btn.configure(command=self.enable_pan_mode)
            
            if icon_name == "ArrowRight":
                btn.configure(command=self.enable_arrow_mode)
            
            if icon_name == "Trash2":
                btn.configure(command=self.delete_selected)

            if icon_name == "ChevronUp":
                btn.configure(command=self.level_up)

            if icon_name == "ChevronDown":
                btn.configure(command=self.level_down)

            if icon_name == "Layers":
                btn.configure(command=self.toggle_layers_panel)

            # Привязываем обработчики для кнопки добавления блока ТОЛЬКО drag-and-drop
            if icon_name == "Square":
                # Убираем команду клика, оставляем только drag-and-drop
                btn.configure(command=None)
                # Добавляем обработчики для drag-and-drop
                btn.bind("<ButtonPress-1>", self.start_drag_from_sidebar)
                btn.bind("<B1-Motion>", self.drag_from_sidebar)
                btn.bind("<ButtonRelease-1>", self.end_drag_from_sidebar)

            self.apply_hover_effect(btn, base_attr="SURFACE")
            btn.pack(pady=8)

    def start_drag_from_sidebar(self, event):
        """Начало перетаскивания из панели инструментов"""
        self.drag_from_sidebar = True
        self.canvas.configure(cursor="crosshair")
        
        # Создаем превью блока
        x = self.canvas.canvasx(event.x_root - self.root.winfo_rootx())
        y = self.canvas.canvasy(event.y_root - self.root.winfo_rooty())
        
        width, height = 150, 80
        self.drag_preview = self.canvas.create_rectangle(
            x - width / 2, y - height / 2,
            x + width / 2, y + height / 2,
            fill="#E3F2FD",
            outline=Colors.PRIMARY,
            width=2,
            dash=(4, 2),
            tags="drag_preview"
        )

    def drag_from_sidebar(self, event):
        """Перетаскивание из панели инструментов"""
        if self.drag_from_sidebar and self.drag_preview:
            # Преобразуем координаты мыши в координаты холста
            x = self.canvas.canvasx(event.x_root - self.root.winfo_rootx())
            y = self.canvas.canvasy(event.y_root - self.root.winfo_rooty())
            
            width, height = 150, 80
            # Обновляем позицию превью
            self.canvas.coords(
                self.drag_preview,
                x - width / 2, y - height / 2,
                x + width / 2, y + height / 2
            )

    def end_drag_from_sidebar(self, event):
        """Завершение перетаскивания из панели инструментов"""
        if self.drag_from_sidebar and self.drag_preview:
            # Преобразуем координаты мыши в координаты холста
            x = self.canvas.canvasx(event.x_root - self.root.winfo_rootx())
            y = self.canvas.canvasy(event.y_root - self.root.winfo_rooty())
            
            # Удаляем превью
            self.canvas.delete(self.drag_preview)
            self.drag_preview = None
            self.drag_from_sidebar = False
            self.canvas.configure(cursor="")
            
            # Создаем новый блок в точке отпускания
            self.create_block_at_position(x, y)

    def create_block_at_position(self, x, y):
        """Создает блок в указанной позиции с учетом текущего уровня"""
        # Базовые размеры
        width, height = 150, 80

        # Создаем блок
        block_id = f"block_{self.next_block_id}"
        self.next_block_id += 1

        # Генерируем код на основе текущего уровня
        parent_id = self.layer_manager.get_current_parent_id()
        current_blocks = self.layer_manager.get_blocks_for_current_level([b["model"] for b in self.blocks])
        
        if parent_id:
            # Находим родительский блок для наследования кода
            parent_block = next((b["model"] for b in self.blocks if b["model"].id == parent_id), None)
            if parent_block:
                # Получаем все блоки на этом уровне с тем же родителем и находим первый свободный номер
                sibling_blocks = [b for b in self.blocks if b["model"].parent_id == parent_id]
                used_numbers = set()
                for block_data in sibling_blocks:
                    code_parts = block_data["model"].code.split(".")
                    if len(code_parts) > 1:
                        try:
                            num = int(code_parts[-1])
                            used_numbers.add(num)
                        except ValueError:
                            pass
                # Находим первый свободный номер
                code_num = 1
                while code_num in used_numbers:
                    code_num += 1
                code = f"{parent_block.code}.{code_num}"
            else:
                # Находим первый свободный номер на корневом уровне
                used_numbers = set()
                for block_data in current_blocks:
                    code = block_data.code
                    if code.startswith("A") and "." not in code:
                        try:
                            num = int(code[1:])
                            used_numbers.add(num)
                        except ValueError:
                            pass
                # Находим первый свободный номер
                code_num = 1
                while code_num in used_numbers:
                    code_num += 1
                code = f"A{code_num}"
        else:
            # Корневой уровень - находим первый свободный номер
            used_numbers = set()
            for block_data in current_blocks:
                code = block_data.code
                if code.startswith("A") and "." not in code:
                    try:
                        num = int(code[1:])
                        used_numbers.add(num)
                    except ValueError:
                        pass
            # Находим первый свободный номер
            code_num = 1
            while code_num in used_numbers:
                code_num += 1
            code = f"A{code_num}"

        # Создаем модель блока
        block_model = Block(
            block_id=block_id,
            name=f"Блок {code}"[:80],  # Ограничиваем имя до 80 символов
            code=code,
            x=x,
            y=y,
            width=width,
            height=height,
            parent_id=parent_id
        )

        # Рисуем прямоугольник
        rect = self.canvas.create_rectangle(
        x - width / 2, y - height / 2,
        x + width / 2, y + height / 2,
        fill=block_model.color,
        outline=Colors.BLOCK_BORDER,
        width=block_model.border_width,  # ← использовать border_width из модели
        tags=("block", block_id)
        )
        

        # Добавляем текст с автопереносом
        formatted_text = self.format_block_text(block_model.name, width)
        text = self.canvas.create_text(
            x, y,
            text=formatted_text,
            font=("Segoe UI", 10),
            fill=Colors.TEXT_PRIMARY,
            justify="center",
            width=width - 10,  # Отступы по 5px с каждой стороны
            tags=("block_text", block_id)
        )

        # Сохраняем информацию о блоке
        block_data = {
            "id": block_id,
            "model": block_model,
            "rect_id": rect,
            "text_id": text,
            "resize_handles": {}  # маркеры изменения размера
        }

        self.blocks.append(block_data)

        # Делаем блок перемещаемым и выбираемым
        self.make_block_interactive(block_data)

        # Проверяем, что блок принадлежит текущему уровню перед отображением
        # (новый блок всегда должен быть виден, так как он создается на текущем уровне)
        # Автоматически выбираем новый блок
        self.select_block(block_data)
        
        # Проверяем ошибки нумерации после создания блока
        self.root.after(100, self.check_numbering_errors)

        # Сохраняем состояние для undo
        self.save_state()

        print(f"Добавлен новый блок через drag-and-drop: {block_id}")
        print(f"Всего блоков: {len(self.blocks)}")
        
        return block_data

    def enable_select_mode(self):
        """Включает режим выбора элементов"""
        if self.current_mode != "select":
            self.current_mode = "select"
            self.is_panning = False
            self.arrow_drawing_mode = False
            self.arrow_start_block = None
            if self.arrow_preview_line:
                self.canvas.delete(self.arrow_preview_line)
                self.arrow_preview_line = None
            self.canvas.configure(cursor="")
            print("Включен режим выбора")

    def enable_pan_mode(self):
        """Включает режим панорамирования"""
        if self.current_mode != "pan":
            self.current_mode = "pan"
            self.is_panning = True
            self.arrow_drawing_mode = False
            self.arrow_start_block = None
            self.canvas.configure(cursor="hand2")
            print("Включен режим панорамирования")
    
    def enable_arrow_mode(self):
        """Включает режим рисования стрелок"""
        if self.current_mode != "draw_arrow":
            self.current_mode = "draw_arrow"
            self.is_panning = False
            self.arrow_drawing_mode = True
            self.arrow_start_block = None
            self.arrow_start_x = None
            self.arrow_start_y = None
            self.arrow_drawing = False
            if self.arrow_preview_line:
                self.canvas.delete(self.arrow_preview_line)
                self.arrow_preview_line = None
            self.canvas.configure(cursor="crosshair")
            print("Включен режим рисования стрелок")

    def create_resize_handles(self, block_data):
        """Создает маркеры для изменения размера блока"""
        # Удаляем старые маркеры
        self.delete_resize_handles(block_data)
        
        model = block_data["model"]
        size = self.resize_handle_size
        
        # Угловые маркеры
        handles_positions = {
            "nw": (model.x - model.width/2, model.y - model.height/2),
            "ne": (model.x + model.width/2, model.y - model.height/2),
            "sw": (model.x - model.width/2, model.y + model.height/2),
            "se": (model.x + model.width/2, model.y + model.height/2)
        }
        
        for handle_type, (x, y) in handles_positions.items():
            # Используем круглые маркеры (как у стрелок)
            handle = self.canvas.create_oval(
                x - size/2, y - size/2,
                x + size/2, y + size/2,
                fill=Colors.PRIMARY,
                outline=Colors.SURFACE,
                width=1,
                tags=("resize_handle", block_data["id"], f"handle_{handle_type}")
            )
            block_data["resize_handles"][handle_type] = handle
            
            # ВАЖНО: Поднимаем маркер наверх, чтобы он был поверх блока
            self.canvas.tag_raise(handle)
            
            # Привязываем обработчики событий для маркера
            self.canvas.tag_bind(handle, "<ButtonPress-1>", 
                               lambda e, b=block_data, h=handle_type: self.start_resize(e, b, h))
            self.canvas.tag_bind(handle, "<B1-Motion>", 
                               lambda e, b=block_data, h=handle_type: self.do_resize(e, b, h))
            self.canvas.tag_bind(handle, "<ButtonRelease-1>", 
                               lambda e, b=block_data: self.end_resize(e, b))
        
        # ВАЖНО: Поднимаем все маркеры наверх в конце
        for handle_id in block_data.get("resize_handles", {}).values():
            try:
                self.canvas.tag_raise(handle_id)
            except tk.TclError:
                pass

    def delete_resize_handles(self, block_data):
        """Удаляет маркеры изменения размера"""
        for handle_id in block_data["resize_handles"].values():
            self.canvas.delete(handle_id)
        block_data["resize_handles"] = {}

    def start_resize(self, event, block_data, handle_type):
        """Начало изменения размера"""
        if self.current_mode == "select":
            self.resizing_block = block_data
            model = block_data["model"]
            
            # Вычисляем координаты углов блока
            left = model.x - model.width / 2
            right = model.x + model.width / 2
            top = model.y - model.height / 2
            bottom = model.y + model.height / 2
            
            # Определяем противоположный угол (фиксированный)
            if handle_type == "nw":  # северо-запад - фиксируем юго-восток
                fixed_x, fixed_y = right, bottom
            elif handle_type == "ne":  # северо-восток - фиксируем юго-запад
                fixed_x, fixed_y = left, bottom
            elif handle_type == "sw":  # юго-запад - фиксируем северо-восток
                fixed_x, fixed_y = right, top
            else:  # se - юго-восток - фиксируем северо-запад
                fixed_x, fixed_y = left, top
            
            # ВАЖНО: Поднимаем блок наверх перед созданием превью, чтобы обводка была видна
            self._raise_block(block_data)
            
            # Создаем превью для растягивания
            self.resize_preview = self.canvas.create_rectangle(
                left, top, right, bottom,
                fill=model.color,
                outline=Colors.PRIMARY,
                width=2,
                dash=(4, 2),
                tags="resize_preview"
            )
            
            block_data["resize_data"] = {
                "handle_type": handle_type,
                "fixed_x": fixed_x,  # Фиксированный угол
                "fixed_y": fixed_y,
                "start_left": left,
                "start_right": right,
                "start_top": top,
                "start_bottom": bottom
            }
            return "break"

    def do_resize(self, event, block_data, handle_type):
        """Изменение размера блока (пока только превью)"""
        if self.resizing_block == block_data and "resize_data" in block_data and self.resize_preview:
            resize_data = block_data["resize_data"]
            
            # Текущая позиция мыши - это новый угол блока
            new_x = event.x
            new_y = event.y
            
            # Фиксированный угол (противоположный)
            fixed_x = resize_data["fixed_x"]
            fixed_y = resize_data["fixed_y"]
            
            # Вычисляем новые координаты углов
            # Минимальные размеры
            min_width = 50
            min_height = 30
            
            # Определяем новые координаты в зависимости от угла
            if handle_type == "nw":  # северо-запад
                new_left = min(new_x, fixed_x - min_width)
                new_top = min(new_y, fixed_y - min_height)
                new_right = fixed_x
                new_bottom = fixed_y
            elif handle_type == "ne":  # северо-восток
                new_left = fixed_x
                new_top = min(new_y, fixed_y - min_height)
                new_right = max(new_x, fixed_x + min_width)
                new_bottom = fixed_y
            elif handle_type == "sw":  # юго-запад
                new_left = min(new_x, fixed_x - min_width)
                new_top = fixed_y
                new_right = fixed_x
                new_bottom = max(new_y, fixed_y + min_height)
            else:  # se - юго-восток
                new_left = fixed_x
                new_top = fixed_y
                new_right = max(new_x, fixed_x + min_width)
                new_bottom = max(new_y, fixed_y + min_height)
            
            # Обновляем превью
            self.canvas.coords(self.resize_preview, new_left, new_top, new_right, new_bottom)
            
            return "break"

    def end_resize(self, event, block_data):
        """Завершение изменения размера - применяем изменения"""
        if self.resizing_block == block_data and "resize_data" in block_data and self.resize_preview:
            resize_data = block_data["resize_data"]
            model = block_data["model"]
            handle_type = resize_data["handle_type"]
            
            # Текущая позиция мыши - это новый угол блока
            new_x = event.x
            new_y = event.y
            
            # Фиксированный угол (противоположный)
            fixed_x = resize_data["fixed_x"]
            fixed_y = resize_data["fixed_y"]
            
            # Минимальные размеры
            min_width = 50
            min_height = 30
            
            # Вычисляем новые координаты углов
            if handle_type == "nw":  # северо-запад
                new_left = min(new_x, fixed_x - min_width)
                new_top = min(new_y, fixed_y - min_height)
                new_right = fixed_x
                new_bottom = fixed_y
            elif handle_type == "ne":  # северо-восток
                new_left = fixed_x
                new_top = min(new_y, fixed_y - min_height)
                new_right = max(new_x, fixed_x + min_width)
                new_bottom = fixed_y
            elif handle_type == "sw":  # юго-запад
                new_left = min(new_x, fixed_x - min_width)
                new_top = fixed_y
                new_right = fixed_x
                new_bottom = max(new_y, fixed_y + min_height)
            else:  # se - юго-восток
                new_left = fixed_x
                new_top = fixed_y
                new_right = max(new_x, fixed_x + min_width)
                new_bottom = max(new_y, fixed_y + min_height)
            
            # Вычисляем новые размеры и центр
            new_width = new_right - new_left
            new_height = new_bottom - new_top
            new_center_x = (new_left + new_right) / 2
            new_center_y = (new_top + new_bottom) / 2
            
            # Применяем изменения к модели
            model.width = new_width
            model.height = new_height
            model.x = new_center_x
            model.y = new_center_y
            
            # Удаляем превью
            self.canvas.delete(self.resize_preview)
            self.resize_preview = None
            
            # Обновляем визуальное представление блока
            self.update_block_visual(block_data)
            
            # ВАЖНО: Поднимаем все маркеры наверх после изменения размера
            for handle_id in block_data.get("resize_handles", {}).values():
                try:
                    self.canvas.tag_raise(handle_id)
                except tk.TclError:
                    pass
            
            # Обновляем стрелки, соединенные с этим блоком
            self.update_arrows_for_block(block_data["id"])
            
            # Обновляем свойства
            if self.selected_block == block_data:
                self.properties_panel.update_properties(model)
            
            del block_data["resize_data"]
            self.resizing_block = None
            
            # Сохраняем состояние для undo
            self.save_state()
            
            print(f"Блок {block_data['id']} изменен до размера {model.width}x{model.height}")

    def update_block_visual(self, block_data):
        """Обновляет визуальное представление блока"""
        model = block_data["model"]
        
        # Обновляем прямоугольник
        x1 = model.x - model.width / 2
        y1 = model.y - model.height / 2
        x2 = model.x + model.width / 2
        y2 = model.y + model.height / 2
        self.canvas.coords(block_data["rect_id"], x1, y1, x2, y2)
        
        # Обновляем текст с автопереносом
        formatted_text = self.format_block_text(model.name, model.width)
        self.canvas.coords(block_data["text_id"], model.x, model.y)
        self.canvas.itemconfig(block_data["text_id"], 
                             text=formatted_text,
                             width=model.width - 10)
        
        # Обновляем маркеры изменения размера
        if block_data == self.selected_block:
            self.create_resize_handles(block_data)
            # ВАЖНО: Убеждаемся, что выбранный блок всегда наверху после любых обновлений
            self._raise_block(block_data)
            # Поднимаем все маркеры наверх
            for handle_id in block_data.get("resize_handles", {}).values():
                try:
                    self.canvas.tag_raise(handle_id)
                except tk.TclError:
                    pass
        
        # Обновляем стрелки, соединенные с этим блоком
        self.update_arrows_for_block(block_data["id"])
        
        # Обновляем точки прикрепления, если они показаны
        self.update_attachment_points()

    def make_block_interactive(self, block_data):
        """Делает блок перемещаемым по холсту и выбираемым"""
        def start_drag(event):
            # Не начинаем перетаскивание в режиме рисования стрелок
            if self.current_mode == "draw_arrow":
                return None
            if self.current_mode == "select":
                # Преобразуем координаты мыши в координаты холста
                x = self.canvas.canvasx(event.x)
                y = self.canvas.canvasy(event.y)
                block_data["drag_data"] = {"x": x, "y": y}
                self.dragging_block = block_data
                # Останавливаем распространение события
                return "break"
            return None

        def drag(event):
            if (self.current_mode == "select" and 
                self.dragging_block == block_data and 
                "drag_data" in block_data):
                # Преобразуем координаты мыши в координаты холста
                x = self.canvas.canvasx(event.x)
                y = self.canvas.canvasy(event.y)
                
                # Вычисляем смещение
                dx = x - block_data["drag_data"]["x"]
                dy = y - block_data["drag_data"]["y"]

                # Обновляем позицию блока в модели
                block_data["model"].x += dx
                block_data["model"].y += dy

                # Перемещаем прямоугольник и текст
                self.canvas.move(block_data["rect_id"], dx, dy)
                self.canvas.move(block_data["text_id"], dx, dy)

                # Обновляем маркеры изменения размера
                if block_data == self.selected_block:
                    for handle_id in block_data["resize_handles"].values():
                        self.canvas.move(handle_id, dx, dy)

                # Обновляем данные о перетаскивании
                block_data["drag_data"] = {"x": x, "y": y}

                # Обновляем стрелки, соединенные с этим блоком
                self.update_arrows_for_block(block_data["id"])
                
                # Обновляем точки прикрепления, если они показаны
                self.update_attachment_points()

                # Обновляем свойства позиции и позицию кнопок действий
                if self.selected_block == block_data:
                    self.properties_panel.update_properties(block_data["model"])
                    self.update_block_action_buttons_position(block_data)
                
                # Останавливаем распространение события
                return "break"

        def end_drag(event):
            if self.dragging_block == block_data and "drag_data" in block_data:
                del block_data["drag_data"]
                self.dragging_block = None
                
                # Сохраняем состояние для undo
                self.save_state()
                
                print(f"Блок {block_data['id']} перемещен в ({block_data['model'].x:.1f}, {block_data['model'].y:.1f})")

        def double_click(event):
            """Обработчик двойного клика для выбора блока"""
            if self.current_mode == "select":
                self.select_block(block_data)
                return "break"
        
        def arrow_click(event):
            """Обработчик клика по блоку в режиме рисования стрелок"""
            # В режиме рисования стрелок — пропускаем дальше (обработает on_canvas_click)
            if self.current_mode == "draw_arrow":
                return None
            # В обычном режиме выбора — сразу выбираем блок по одиночному клику
            if self.current_mode == "select":
                self.select_block(block_data)
                return "break"
            return None

        # Привязываем обработчики событий
        # Важно: arrow_click должен быть первым, чтобы перехватывать клики в режиме рисования стрелок
        for item_id in [block_data["rect_id"], block_data["text_id"]]:
            self.canvas.tag_bind(item_id, "<Button-1>", arrow_click)  # Сначала обработчик стрелок
            self.canvas.tag_bind(item_id, "<ButtonPress-1>", start_drag)
            self.canvas.tag_bind(item_id, "<B1-Motion>", drag)
            self.canvas.tag_bind(item_id, "<ButtonRelease-1>", end_drag)
            self.canvas.tag_bind(item_id, "<Double-Button-1>", double_click)

    def select_block(self, block_data):
        """Выбирает блок и обновляет панель свойств"""
        # Проверяем, что блок принадлежит текущему уровню
        current_blocks = self.layer_manager.get_blocks_for_current_level([b["model"] for b in self.blocks])
        if block_data["model"] not in current_blocks:
            print(f"Блок {block_data['model'].code} не принадлежит текущему уровню")
            return
        
        # Если открыто меню настроек, закрываем его
        if hasattr(self, 'settings_menu') and self.settings_menu and self.settings_menu.winfo_exists():
            try:
                grid_info = self.settings_menu.grid_info()
                if grid_info:
                    self.close_settings_menu()
            except:
                pass
        
        # Сбрасываем выделение предыдущего блока
        if self.selected_block:
            prev_model = self.selected_block["model"]
            self.canvas.itemconfig(
                self.selected_block["rect_id"],
                outline=Colors.BLOCK_BORDER,
                width=prev_model.border_width
            )
            self.delete_resize_handles(self.selected_block)
            self.hide_block_action_buttons()
        
        # Сбрасываем выделение стрелки, если была выбрана
        if self.selected_arrow:
            self.deselect_arrow()
        
        # Выделяем новый блок
        self.selected_block = block_data
        self.canvas.itemconfig(block_data["rect_id"], outline=Colors.PRIMARY, width=3)
        
        # ВАЖНО: Поднимаем блок наверх, чтобы обводка выделения была видна
        self._raise_block(block_data)
        
        # Создаем маркеры изменения размера
        self.create_resize_handles(block_data)
        # ВАЖНО: Поднимаем все маркеры наверх, чтобы они были поверх блока
        for handle_id in block_data.get("resize_handles", {}).values():
            try:
                self.canvas.tag_raise(handle_id)
            except tk.TclError:
                pass

        # Кнопки действий справа от блока
        self.show_block_action_buttons(block_data)
        
        # Обновляем панель свойств
        self.properties_panel.update_properties(block_data["model"])
        
        print(f"Выбран блок: {block_data['id']}")

    def select_arrow(self, arrow_data):
        """Выбирает стрелку и обновляет панель свойств"""
        # Если открыто меню настроек, закрываем его
        if hasattr(self, 'settings_menu') and self.settings_menu and self.settings_menu.winfo_exists():
            try:
                grid_info = self.settings_menu.grid_info()
                if grid_info:
                    self.close_settings_menu()
            except:
                pass
        
        # Сбрасываем выделение предыдущей стрелки
        if self.selected_arrow:
            self.deselect_arrow()
        
        # Сбрасываем выделение блока, если был выбран
        if self.selected_block:
            prev_model = self.selected_block["model"]
            self.canvas.itemconfig(
                self.selected_block["rect_id"],
                outline=Colors.BLOCK_BORDER,
                width=prev_model.border_width
            )
            self.delete_resize_handles(self.selected_block)
            self.selected_block = None
            self.hide_block_action_buttons()
        
        # Выделяем новую стрелку
        self.selected_arrow = arrow_data
        arrow = arrow_data["arrow"]
        
        # Увеличиваем толщину линии для выделения
        if arrow_data.get("line_id"):
            self.canvas.itemconfig(arrow_data["line_id"], width=arrow.width + 2)
        
        # Показываем кнопки действий и маркеры для перетаскивания
        self.show_arrow_action_buttons(arrow_data)
        self.create_arrow_drag_handles(arrow_data)
        
        # Обновляем панель свойств
        self.properties_panel.update_properties(arrow)
        
        print(f"Выбрана стрелка: {arrow.id}")
    
    def deselect_arrow(self):
        """Снимает выделение со стрелки"""
        if self.selected_arrow:
            arrow = self.selected_arrow["arrow"]
            # Восстанавливаем обычную толщину линии
            if self.selected_arrow.get("line_id"):
                self.canvas.itemconfig(self.selected_arrow["line_id"], width=arrow.width)
            # Скрываем кнопки действий и маркеры
            self.hide_arrow_action_buttons()
            self.delete_arrow_drag_handles()
            self.hide_attachment_points()
            self.selected_arrow = None
    
    def on_arrow_click(self, event):
        """Обработчик клика по стрелке"""
        if self.current_mode == "select":
            # Преобразуем координаты мыши в координаты холста
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Находим элемент под курсором
            item_id = self.canvas.find_closest(x, y)[0]
            tags = self.canvas.gettags(item_id)
            
            arrow_id = None
            for tag in tags:
                if tag.startswith("arrow_") and tag != "arrow_line" and tag != "arrow_arrowhead" and tag != "arrow_hitbox":
                    arrow_id = tag
                    break
            
            if arrow_id:
                arrow_data = next((a for a in self.arrows if a["arrow"].id == arrow_id), None)
                if arrow_data:
                    self.select_arrow(arrow_data)
                    return "break"

    def on_properties_change(self, element, update_data):
        """Обработчик изменений в свойствах элемента (блока или стрелки)"""
        
        # Обновляем модель элемента
        element.update_from_dict(update_data)
        
        # Обработка блоков
        if isinstance(element, Block):
            # Ограничиваем все текстовые поля до 80 символов
            if "name" in update_data and len(update_data["name"]) > 80:
                update_data["name"] = update_data["name"][:80]
            if "description" in update_data and len(update_data["description"]) > 80:
                update_data["description"] = update_data["description"][:80]
            if "element_type" in update_data and len(update_data["element_type"]) > 80:
                update_data["element_type"] = update_data["element_type"][:80]
            
            # Находим визуальное представление блока
            block_data = next((b for b in self.blocks if b["model"] == element), None)
            if block_data:
                # Обработка изменения кода
                if "code" in update_data:
                    old_code = element.code
                    new_code = update_data["code"]
                    
                    # Проверяем, не конфликтует ли новый код с существующим блоком
                    conflicting_block = next(
                        (b for b in self.blocks 
                         if b["model"].code == new_code and b["model"].id != element.id 
                         and b["model"].parent_id == element.parent_id),
                        None
                    )
                    
                    if conflicting_block:
                        # Сдвигаем конфликтующий блок и всех его детей
                        self._shift_block_and_children(conflicting_block)
                    
                    # Обновляем код блока
                    element.code = new_code
                    element.name = f"Блок {new_code}"
                    
                    # Обновляем все дочерние блоки рекурсивно
                    self._update_children_codes_recursive(block_data, old_code, new_code)
                    
                    # Обновляем текст на canvas
                    model = block_data["model"]
                    formatted_text = self.format_block_text(element.name, model.width)
                    self.canvas.itemconfig(block_data["text_id"], 
                                         text=formatted_text,
                                         width=model.width - 10)
                
                # Обновляем визуальное представление
                if "name" in update_data:
                    model = block_data["model"]
                    # Ограничиваем имя до 80 символов
                    name_text = update_data["name"][:80] if len(update_data["name"]) > 80 else update_data["name"]
                    formatted_text = self.format_block_text(name_text, model.width)
                    self.canvas.itemconfig(block_data["text_id"], 
                                         text=formatted_text,
                                         width=model.width - 10)
                
                if "color" in update_data:
                    self.canvas.itemconfig(block_data["rect_id"], fill=update_data["color"])
                
                if "border_width" in update_data:
                    self.canvas.itemconfig(block_data["rect_id"], width=update_data["border_width"])
                
                if any(key in update_data for key in ["x", "y", "width", "height"]):
                    self.update_block_visual(block_data)
                
                # ВАЖНО: Обновляем обводку выбранного элемента
                if self.selected_block == block_data:
                    # Устанавливаем выделенную обводку для выбранного элемента
                    self.canvas.itemconfig(block_data["rect_id"], outline=Colors.PRIMARY, width=element.border_width)
                    # ВАЖНО: Поднимаем выбранный блок наверх, чтобы обводка выделения была видна
                    self._raise_block(block_data)
                    # Обновляем маркеры изменения размера
                    self.create_resize_handles(block_data)
                
                print(f"Обновлен блок {block_data['id']}: {update_data}")
                
                # Проверяем ошибки нумерации после изменения свойств
                self.check_numbering_errors()
        
        # Обработка стрелок
        elif isinstance(element, Arrow):
            # Ограничиваем текст стрелки до 80 символов
            if "text" in update_data and len(update_data["text"]) > 80:
                update_data["text"] = update_data["text"][:80]
            
            # Находим визуальное представление стрелки
            arrow_data = next((a for a in self.arrows if a["arrow"] == element), None)
            if arrow_data:
                # Обновляем свойства стрелки
                element.update_from_dict(update_data)
                
                # Перерисовываем стрелку с новыми свойствами
                self.draw_arrow(arrow_data)
                
                # Если стрелка выбрана, обновляем выделение и маркеры
                if self.selected_arrow == arrow_data:
                    self.update_arrow_drag_handles(arrow_data)
                    self.update_arrow_action_buttons_position(arrow_data)
            
            print(f"Обновлена стрелка {element.id}: {update_data}")

    def load_icon(self, name, size, force_original=False, recolor=None):
        """Загрузка PNG-иконки с безопасным фолбеком и кэшем.
        Поддерживает имена вида Name.png, Name (1).png, Name (2).png.

        force_original=True — не перекрашивать иконку в тёмной теме
        (оставить исходные цвета PNG, например зелёный/красный).
        """
        theme_key = "orig" if force_original else ("dark" if self.is_dark_theme else "light")
        recolor_key = ""
        if recolor:
            recolor_key = f"_{recolor[0]}_{recolor[1]}_{recolor[2]}_{recolor[3]}"
        cache_key = f"{name}_{size[0]}x{size[1]}_{theme_key}{recolor_key}"
        if cache_key in self._icons:
            return self._icons[cache_key]
        base_dir = os.path.dirname(__file__)
        candidates = [
            os.path.join(base_dir, "img", f"{name}.png"),
            os.path.join(base_dir, "img", f"{name} (1).png"),
            os.path.join(base_dir, "img", f"{name} (2).png")
        ]
        path = next((p for p in candidates if os.path.exists(p)), None)
        try:
            if path is None:
                raise FileNotFoundError
            img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
            # Если явно задан цвет перекраски — используем его
            if recolor:
                img = self._recolor_icon(img, recolor)
            # Для тёмной темы перекрашиваем в белый только если не запрошен оригинал
            elif self.is_dark_theme and not force_original:
                img = self._recolor_icon(img, (255, 255, 255, 255))
            self._icons[cache_key] = ImageTk.PhotoImage(img)
        except Exception:
            from PIL import Image as PILImage
            # Прозрачный фолбек нужного размера
            fallback = PILImage.new("RGBA", size, (0, 0, 0, 0))
            self._icons[cache_key] = ImageTk.PhotoImage(fallback)
        return self._icons[cache_key]

    def _recolor_icon(self, image, rgba_color):
        """Возвращает копию изображения, закрашенную указанным цветом с сохранением альфы."""
        base = Image.new("RGBA", image.size, rgba_color)
        alpha = image.getchannel("A") if "A" in image.getbands() else None
        if alpha is not None:
            base.putalpha(alpha)
        return base

    def setup_canvas(self, parent):
        """Область холста с сеткой и A0 блоком"""
        canvas_frame = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=12)
        self.canvas_frame = canvas_frame

        # Canvas с прокруткой
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=Colors.SURFACE,
            highlightthickness=0,
            scrollregion=(-2000, -2000, 4000, 4000),  # Большая область для панорамирования
            takefocus=True  # Разрешаем canvas получать фокус для горячих клавиш
        )
        
        # Добавляем скроллбары
        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещаем элементы
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Рисуем сетку на всей области холста
        self.draw_grid()
        
        # Отрисовываем все стрелки после создания canvas
        self.root.after(100, self.draw_all_arrows)

        # Footer note
        self.footer_label = tk.Label(
            canvas_frame,
            text="Диаграмма: Пример IDEF0 | Масштаб: 100%",
            font=("Segoe UI", 9),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.SURFACE
        )
        # Привязываем к нижнему левому углу контейнера
        self.footer_label.place(relx=0, rely=1, x=14, y=-10, anchor='sw')
        
        # Footer для отображения текущего уровня
        self.footer_right_label = tk.Label(
            canvas_frame,
            text="Уровень 0",
            font=("Segoe UI", 9),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.SURFACE
        )
        self.footer_right_label.place(relx=1, rely=1, x=-14, y=-10, anchor='se')
        
        # Плашка с ошибкой (круг с восклицательным знаком) в нижнем правом углу
        # Создаем Canvas для круга
        self.error_indicator_canvas = tk.Canvas(
            canvas_frame,
            width=24,
            height=24,
            bg=Colors.SURFACE,
            highlightthickness=0,
            cursor="hand2"
        )
        self.error_indicator_canvas.place(relx=1, rely=1, x=-40, y=-30, anchor='se')
        self.error_indicator_canvas.place_forget()  # Скрываем по умолчанию
        
        # Рисуем круг с тускло красным фоном
        self.error_circle_id = self.error_indicator_canvas.create_oval(
            2, 2, 22, 22,
            fill="#ffcccc",  # Тускло красный
            outline="#ff9999",
            width=1
        )
        
        # Рисуем ярко красный восклицательный знак
        self.error_exclamation_id = self.error_indicator_canvas.create_text(
            12, 12,
            text="!",
            font=("Segoe UI", 14, "bold"),
            fill="#ff0000",  # Ярко красный
            anchor="center"
        )
        
        # Tooltip для плашки ошибки
        self.error_tooltip = None
        self.error_indicator_canvas.bind("<Enter>", self._show_error_tooltip)
        self.error_indicator_canvas.bind("<Leave>", self._hide_error_tooltip)
        
        # Обновляем footer после создания
        self.root.after(100, self.update_footer_info)
        # Проверяем ошибки после создания
        self.root.after(200, self.check_numbering_errors)
        
        # Плашка с кнопками undo/redo и копирование/вставка в рабочей области
        self.create_workspace_toolbar(canvas_frame)

        # Привязка к событиям клавиатуры
        self.canvas.bind_all("<KeyPress-space>", self.on_space_press)
        self.canvas.bind_all("<KeyRelease-space>", self.on_space_release)
        # Масштабирование колесиком с Ctrl
        self.canvas.bind_all("<Control-MouseWheel>", self.on_ctrl_mousewheel)
        # Для трекпадов/альтернатив (Linux/X11 могут использовать Button-4/5 с Control)
        self.canvas.bind_all("<Control-Button-4>", lambda e: self.on_ctrl_scroll_steps(1))
        self.canvas.bind_all("<Control-Button-5>", lambda e: self.on_ctrl_scroll_steps(-1))

        # Обработчик клика по пустому месту для сброса выделения
        # Устанавливаем фокус на canvas при клике для работы горячих клавиш
        def canvas_click_with_focus(e):
            self.canvas.focus_set()
            return self.on_canvas_click(e)
        self.canvas.bind("<Button-1>", canvas_click_with_focus)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Обработчик движения мыши для превью стрелки
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Привязываем обработчики для выбора стрелок
        self.canvas.tag_bind("arrow_line", "<Button-1>", self.on_arrow_click)
        self.canvas.tag_bind("arrow_hitbox", "<Button-1>", self.on_arrow_click)
        self.canvas.tag_bind("arrow_arrowhead", "<Button-1>", self.on_arrow_click)
        
        # Привязываем горячие клавиши после создания canvas
        self.setup_hotkeys()

    def create_workspace_toolbar(self, parent):
        """Создает плашку с кнопками undo/redo и копирование/вставка в рабочей области"""
        # Создаем контейнер для плашки
        toolbar_panel = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        # Размещаем в верхнем левом углу
        toolbar_panel.place(relx=0, rely=0, x=12, y=12, anchor='nw')
        
        # Внутренний фрейм для кнопок
        buttons_frame = tk.Frame(toolbar_panel, bg=Colors.SURFACE)
        buttons_frame.pack(padx=4, pady=4)
        
        # Кнопка Undo
        undo_btn = tk.Button(
            buttons_frame,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=self.undo
        )
        self.set_widget_icon(undo_btn, "Undo", (20, 20))
        undo_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(undo_btn)
        self.undo_btn = undo_btn
        
        # Кнопка Redo
        redo_btn = tk.Button(
            buttons_frame,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=self.redo
        )
        self.set_widget_icon(redo_btn, "Redo", (20, 20))
        redo_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(redo_btn)
        self.redo_btn = redo_btn
        
        # Разделитель
        separator = tk.Frame(buttons_frame, bg=Colors.BORDER, width=1)
        separator.pack(side=tk.LEFT, padx=4, fill=tk.Y, pady=2)
        
        # Кнопка Вырезать
        cut_btn = tk.Button(
            buttons_frame,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=self.cut_selected
        )
        self.set_widget_icon(cut_btn, "virez", (20, 20))
        cut_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(cut_btn)
        self.cut_btn = cut_btn
        
        # Кнопка Копировать
        copy_btn = tk.Button(
            buttons_frame,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=self.copy_selected
        )
        self.set_widget_icon(copy_btn, "Copy", (20, 20))
        copy_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(copy_btn)
        self.copy_btn = copy_btn
        
        # Кнопка Вставить
        paste_btn = tk.Button(
            buttons_frame,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=self.paste_clipboard
        )
        self.set_widget_icon(paste_btn, "vstavka", (20, 20))
        paste_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(paste_btn)
        self.paste_btn = paste_btn
        
        # Сохраняем ссылку на панель для обновления темы
        self.workspace_toolbar = toolbar_panel
        
        # Обновляем состояние кнопок undo/redo
        self.update_undo_redo_buttons()
        
        # Инициализируем переменную для меню настроек
        self.settings_menu = None

    def open_settings_menu(self):
        """Открывает меню настроек вместо панели свойств"""
        # Если меню уже создано и видимо, закрываем его (переключаем обратно на панель свойств)
        if hasattr(self, 'settings_menu') and self.settings_menu and self.settings_menu.winfo_exists():
            try:
                # Проверяем, видимо ли меню (grid_info возвращает словарь, если виджет размещен через grid)
                grid_info = self.settings_menu.grid_info()
                if grid_info:
                    self.close_settings_menu()
                    return
            except:
                pass
        
        # Создаем или показываем меню настроек
        self.create_settings_menu()
    
    def create_settings_menu(self):
        """Создает меню настроек вместо панели свойств"""
        # Скрываем панель свойств
        if hasattr(self, 'properties_panel'):
            self.properties_panel.grid_remove()
        
        # Получаем main_frame для размещения меню
        main_frame = self.main_frame
        
        # Создаем контейнер для меню настроек (в том же месте, где панель свойств)
        if not hasattr(self, 'settings_menu') or not self.settings_menu or not self.settings_menu.winfo_exists():
            # Внешняя панель с границами, как у sidebar
            settings_panel = tk.Frame(
                main_frame,
                bg=Colors.SURFACE,
                width=Dimensions.PROPERTIES_WIDTH,
                highlightthickness=1,
                highlightbackground=Colors.BORDER,
                takefocus=False  # Не получает фокус
            )
            settings_panel.pack_propagate(False)
            settings_panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
            
            # Создаем внутренний контейнер
            main_content = tk.Frame(
                settings_panel,
                bg=Colors.SURFACE,
                highlightthickness=0,
                takefocus=False  # Не получает фокус
            )
            main_content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            self.settings_menu = settings_panel
            self.settings_main_content = main_content
        else:
            # Если меню уже существует, обновляем его цвета и пересоздаем содержимое
            settings_panel = self.settings_menu
            # Обновляем цвета панели и границы
            settings_panel.configure(bg=Colors.SURFACE, highlightbackground=Colors.BORDER)
            main_content = self.settings_main_content
            # Обновляем цвета внутреннего контейнера
            main_content.configure(bg=Colors.SURFACE)
            # Очищаем содержимое
            for widget in main_content.winfo_children():
                widget.destroy()
            # Удаляем старую кнопку закрытия, если она есть
            for widget in settings_panel.winfo_children():
                if isinstance(widget, tk.Button) and widget.winfo_exists():
                    try:
                        widget_text = widget.cget("text")
                        if widget_text == "✕":
                            widget.destroy()
                    except:
                        pass
        
        # Кнопка закрытия (крестик) в верхнем правом углу панели
        close_btn = tk.Button(
            settings_panel,
            text="✕",
            font=("Segoe UI", 16),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            activebackground=Colors.ACTIVE,
            activeforeground=Colors.TEXT_PRIMARY,
            highlightthickness=0,
            command=self.close_settings_menu,
            cursor="hand2"
        )
        close_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-8, y=8)
        self.apply_hover_effect(close_btn)
        
        # Создаем содержимое меню в main_content
        # Основной контейнер для центрирования
        main_container = tk.Frame(main_content, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок меню
        header_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        header_frame.pack(fill=tk.X, padx=16, pady=(16, 12))
        
        # Заголовок
        title_label = tk.Label(
            header_frame,
            text="Настройки",
            font=("Segoe UI", 14, "bold"),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY
        )
        title_label.pack(side=tk.LEFT)
        
        # Контейнер для центрирования кнопок
        center_container = tk.Frame(main_container, bg=Colors.SURFACE)
        center_container.pack(expand=True, fill=tk.BOTH)
        
        # Контейнер для кнопок (с ограниченной шириной для центрирования)
        buttons_frame = tk.Frame(center_container, bg=Colors.SURFACE)
        buttons_frame.pack(expand=True, pady=(0, 16))
        
        # Кнопка Обучение
        learning_btn = tk.Button(
            buttons_frame,
            text="Обучение",
            font=("Segoe UI", 11),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="solid",
            bd=1,
            padx=24,
            pady=14,
            activebackground=Colors.ACTIVE,
            highlightthickness=0,
            borderwidth=1,
            highlightbackground=Colors.BORDER,
            highlightcolor=Colors.BORDER,
            anchor="w",
            command=self.show_learning  # Заглушка, можно добавить функцию позже
        )
        self.set_widget_icon(learning_btn, "BookOpen", (20, 20), compound='left')
        learning_btn.pack(fill=tk.X, pady=(0, 12))
        self.apply_hover_effect(learning_btn)
        
        # Кнопка Документация
        doc_btn = tk.Button(
            buttons_frame,
            text="Документация",
            font=("Segoe UI", 11),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="solid",
            bd=1,
            padx=24,
            pady=14,
            activebackground=Colors.ACTIVE,
            highlightthickness=0,
            borderwidth=1,
            highlightbackground=Colors.BORDER,
            highlightcolor=Colors.BORDER,
            anchor="w",
            command=self.show_documentation
        )
        self.set_widget_icon(doc_btn, "HelpCircle", (20, 20), compound='left')
        doc_btn.pack(fill=tk.X, pady=(0, 12))
        self.apply_hover_effect(doc_btn)
        
        # Кнопка смены темы
        self.theme_toggle_btn = tk.Button(
            buttons_frame,
            text="Тёмная тема",
            font=("Segoe UI", 11),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="solid",
            bd=1,
            padx=24,
            pady=14,
            activebackground=Colors.ACTIVE,
            highlightthickness=0,
            borderwidth=1,
            highlightbackground=Colors.BORDER,
            highlightcolor=Colors.BORDER,
            anchor="w",
            command=self.toggle_theme
        )
        self.theme_toggle_btn.pack(fill=tk.X)
        self.apply_hover_effect(self.theme_toggle_btn)
        self.update_theme_button_label()
        
        # Показываем меню (если оно было скрыто через grid_remove)
        try:
            grid_info = settings_panel.grid_info()
            if not grid_info:
                # Если панель была скрыта через grid_remove, показываем её
                settings_panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        except Exception:
            # Если возникла ошибка, просто пытаемся показать панель
            try:
                settings_panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
            except Exception:
                pass
        
        # Привязываем ESC для закрытия меню
        def on_escape(event):
            self.close_settings_menu()
        settings_panel.bind("<Escape>", on_escape)
        # Не устанавливаем фокус на окно настроек, чтобы оно не выделялось
    
    def close_settings_menu(self):
        """Закрывает меню настроек и показывает панель свойств"""
        # Скрываем меню настроек
        if hasattr(self, 'settings_menu') and self.settings_menu and self.settings_menu.winfo_exists():
            self.settings_menu.grid_remove()
        
        # Показываем панель свойств обратно
        if hasattr(self, 'properties_panel'):
            self.properties_panel.grid()
            
            # Обновляем панель свойств для текущего выбранного элемента
            if self.selected_arrow:
                # Если выбрана стрелка, обновляем панель свойств для стрелки
                self.properties_panel.update_properties(self.selected_arrow["arrow"])
            elif self.selected_block:
                # Если выбран блок, обновляем панель свойств для блока
                self.properties_panel.update_properties(self.selected_block["model"])
            else:
                # Если ничего не выбрано, сбрасываем панель свойств
                self.properties_panel.update_properties(None)
    
    def show_learning(self):
        """Показывает окно обучения (заглушка)"""
        # Можно добавить функциональность позже
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Обучение", "Функция обучения будет добавлена позже")

    # --- Кнопки действий для блока (переместить / копировать / удалить) ---

    def show_block_action_buttons(self, block_data):
        """Создаёт три кнопки справа от выбранного блока на холсте."""
        if not hasattr(self, "canvas"):
            return

        self.hide_block_action_buttons()

        model = block_data["model"]
        # Правая граница блока + отступ
        base_x = model.x + model.width / 2 + 24
        base_y = model.y
        spacing = 32  # расстояние между кнопками

        # Используем ваши PNG: ожидатся файлы без фона в папке img:
        # Close.png (красный крест), Copy.png (две страницы), mov.png (зелёный крест-стрелки)
        buttons_spec = [
            ("move", "Переместить", "mov"),
            ("copy", "Копировать", "Copy"),
            ("delete", "Удалить", "Close"),
        ]

        self.block_action_buttons = []

        for index, (action, tooltip, icon_name) in enumerate(buttons_spec):
            # Текстовые подписи для кнопок возле блока
            if action == "move":
                btn_text = ""
            elif action == "copy":
                btn_text = ""
            else:
                btn_text = ""
            btn = tk.Button(
                self.canvas,
                bg=Colors.SURFACE,  # совпадает с цветом холста
                fg=Colors.TEXT_PRIMARY,
                relief="flat",
                bd=0,
                padx=0,
                pady=0,
                activebackground=Colors.SURFACE,
                highlightthickness=0,
                text=btn_text,
            )
            # Иконка с вашим PNG (файлы Name.png / Name (1).png / Name (2).png в папке img)
            # Показываем и иконку, и текст (слева иконка, справа подпись 1 / Copy / Close)
            compound = "left" if btn_text else "center"
            self.set_widget_icon(btn, icon_name, (24, 24), compound=compound, force_original=True)

            if action == "move":
                # Перемещение самого блока при перетаскивании иконки
                def start_move(ev, b=block_data):
                    self._move_icon_state = {
                        "block": b,
                        "start_x": ev.x_root,
                        "start_y": ev.y_root,
                        "orig_x": b["model"].x,
                        "orig_y": b["model"].y,
                    }

                def do_move(ev, b=block_data):
                    state = getattr(self, "_move_icon_state", None)
                    if not state or state.get("block") is not b:
                        return
                    dx = ev.x_root - state["start_x"]
                    dy = ev.y_root - state["start_y"]

                    model = b["model"]
                    model.x = state["orig_x"] + dx
                    model.y = state["orig_y"] + dy

                    # Обновляем положение прямоугольника и текста
                    self.update_block_visual(b)
                    # Обновляем панель свойств
                    if self.selected_block == b:
                        self.properties_panel.update_properties(model)
                    # Обновляем кнопки действий
                    self.update_block_action_buttons_position(b)

                def end_move(_ev, b=block_data):
                    state = getattr(self, "_move_icon_state", None)
                    if state and state.get("block") is b:
                        self._move_icon_state = None

                btn.bind("<ButtonPress-1>", start_move)
                btn.bind("<B1-Motion>", do_move)
                btn.bind("<ButtonRelease-1>", end_move)

            elif action == "copy":
                btn.configure(command=lambda b=block_data: self.copy_block(b))
            elif action == "delete":
                btn.configure(command=lambda b=block_data: self.delete_block_direct(b))

            # Для этих кнопок не меняем фон при наведении — только PNG-иконка
            self.apply_hover_effect(btn, enable=False)

            # Позиционируем кнопку в canvas
            y = base_y + (index - 1) * spacing
            win_id = self.canvas.create_window(
                base_x,
                y,
                window=btn,
                anchor="w",
                tags=("block_action", f"block_actions_{block_data['id']}"),
            )
            self.block_action_buttons.append({"window_id": win_id, "button": btn, "action": action})

    def update_block_action_buttons_position(self, block_data):
        """Обновляет позицию кнопок действий при перемещении/изменении блока."""
        if not self.block_action_buttons or self.selected_block != block_data:
            return
        model = block_data["model"]
        base_x = model.x + model.width / 2 + 24
        base_y = model.y
        spacing = 32

        for index, data in enumerate(self.block_action_buttons):
            y = base_y + (index - 1) * spacing
            try:
                self.canvas.coords(data["window_id"], base_x, y)
            except tk.TclError:
                continue

    def hide_block_action_buttons(self):
        """Удаляет кнопки действий для блока с холста."""
        if not hasattr(self, "canvas"):
            self.block_action_buttons = []
            return
        for data in self.block_action_buttons:
            try:
                if data.get("window_id"):
                    self.canvas.delete(data["window_id"])
            except tk.TclError:
                pass
            btn = data.get("button")
            if btn is not None and btn.winfo_exists():
                btn.destroy()
        self.block_action_buttons = []

    def copy_block(self, block_data):
        """Создаёт копию блока рядом с исходным."""
        model = block_data["model"]
        offset = 30
        self.create_block_at_position(model.x + offset, model.y + offset)

    def delete_block_direct(self, block_data):
        """Удаление конкретного блока по кнопке (не затрагивает выбранную стрелку)."""
        if block_data not in self.blocks:
            return
        
        # Сохраняем информацию о блоке для перенумерации
        deleted_block = block_data["model"]
        deleted_parent_id = deleted_block.parent_id
        deleted_code = deleted_block.code
        
        # Если этот блок выбран — обновим состояние
        if self.selected_block == block_data:
            self.selected_block = None
            self.properties_panel.update_properties(None)
            self.hide_block_action_buttons()
        
        # Удаляем все дочерние блоки рекурсивно
        self._delete_block_children(block_data["id"])
        
        # Удаляем стрелки, соединенные с этим блоком
        block_id = block_data["id"]
        arrows_to_remove = [a for a in self.arrows if a["arrow"].is_connected_to_block(block_id)]
        for arrow_data in arrows_to_remove:
            self.delete_arrow(arrow_data)
        
        # Удаляем блок с холста
        try:
            self.canvas.delete(block_data["rect_id"])
            self.canvas.delete(block_data["text_id"])
        except tk.TclError:
            pass
        
        # Удаляем маркеры изменения размера
        self.delete_resize_handles(block_data)
        
        # Удаляем блок из списка
        self.blocks.remove(block_data)
        
        # Перенумеровываем оставшиеся блоки на том же уровне
        self._renumber_blocks_after_deletion(deleted_parent_id, deleted_code)
    
    def delete_block(self, block_data):
        """Удаление блока (сохраняет состояние для undo/redo)"""
        if block_data not in self.blocks:
            return
        # Сохраняем состояние перед удалением для undo/redo
        self.save_state()
        self.delete_block_direct(block_data)
        
        # Обновляем canvas для текущего уровня
        self.refresh_canvas()
        
        # Обновляем панель слоев, если она открыта
        if self.layers_panel_visible:
            self.update_layers_tree()
        
        # Проверяем ошибки нумерации после удаления блока
        self.check_numbering_errors()
    
    def _delete_block_children(self, parent_block_id):
        """Рекурсивно удаляет все дочерние блоки"""
        children = [b for b in self.blocks if b["model"].parent_id == parent_block_id]
        for child_block in children:
            # Рекурсивно удаляем детей
            self._delete_block_children(child_block["id"])
            
            # Удаляем стрелки, соединенные с дочерним блоком
            block_id = child_block["id"]
            arrows_to_remove = [a for a in self.arrows if a["arrow"].is_connected_to_block(block_id)]
            for arrow_data in arrows_to_remove:
                self.delete_arrow(arrow_data)
            
            # Удаляем с холста
            try:
                self.canvas.delete(child_block["rect_id"])
                self.canvas.delete(child_block["text_id"])
            except tk.TclError:
                pass
            
            self.delete_resize_handles(child_block)
            self.blocks.remove(child_block)
    
    def _renumber_blocks_after_deletion(self, parent_id, deleted_code):
        """Перенумеровывает блоки после удаления"""
        # Получаем все блоки на том же уровне
        if parent_id is None:
            # Корневой уровень
            sibling_blocks = [b for b in self.blocks if b["model"].parent_id is None]
            # Сортируем по коду
            sibling_blocks.sort(key=lambda b: self._extract_code_number(b["model"].code))
            
            # Перенумеровываем
            for i, block_data in enumerate(sibling_blocks, 1):
                old_code = block_data["model"].code
                new_code = f"A{i}"
                if old_code != new_code:
                    self._update_block_code_recursive(block_data, old_code, new_code)
        else:
            # Уровень с родителем
            sibling_blocks = [b for b in self.blocks if b["model"].parent_id == parent_id]
            # Находим родительский блок
            parent_block = next((b["model"] for b in self.blocks if b["model"].id == parent_id), None)
            if parent_block:
                # Сортируем по номеру в коде
                sibling_blocks.sort(key=lambda b: self._extract_code_number(b["model"].code, parent_block.code))
                
                # Перенумеровываем
                for i, block_data in enumerate(sibling_blocks, 1):
                    old_code = block_data["model"].code
                    new_code = f"{parent_block.code}.{i}"
                    if old_code != new_code:
                        self._update_block_code_recursive(block_data, old_code, new_code)
    
    def _extract_code_number(self, code, parent_code=None):
        """Извлекает номер из кода блока для сортировки"""
        if parent_code:
            # Для дочерних блоков: A1.2 -> 2
            if code.startswith(parent_code + "."):
                try:
                    return int(code.split(".")[-1])
                except ValueError:
                    return 0
        else:
            # Для корневых блоков: A1 -> 1
            if code.startswith("A") and "." not in code:
                try:
                    return int(code[1:])
                except ValueError:
                    return 0
        return 0
    
    def _update_block_code_recursive(self, block_data, old_code, new_code):
        """Обновляет код блока и всех его дочерних блоков"""
        block = block_data["model"]
        block.code = new_code
        block.name = f"Блок {new_code}"
        
        # Обновляем текст на canvas
        if block_data.get("text_id"):
            try:
                formatted_text = self.format_block_text(block.name, block.width)
                self.canvas.itemconfig(block_data["text_id"], text=formatted_text)
            except tk.TclError:
                pass
        
        # Обновляем все дочерние блоки
        children = [b for b in self.blocks if b["model"].parent_id == block.id]
        for child_block_data in children:
            child_old_code = child_block_data["model"].code
            # Заменяем префикс кода
            if child_old_code.startswith(old_code + "."):
                child_new_code = child_old_code.replace(old_code + ".", new_code + ".", 1)
                self._update_block_code_recursive(child_block_data, child_old_code, child_new_code)
        
        # Обновляем панель свойств, если этот блок выбран
        if self.selected_block == block_data:
            self.properties_panel.update_properties(block)
    
    def _shift_block_and_children(self, block_data):
        """Сдвигает блок и всех его дочерних элементов на 1 позицию вперед"""
        block = block_data["model"]
        old_code = block.code
        
        # Определяем новый код (увеличиваем последний номер на 1)
        if "." in old_code:
            # Для дочерних блоков: A1.2 -> A1.3
            parts = old_code.split(".")
            try:
                last_num = int(parts[-1])
                new_code = ".".join(parts[:-1]) + "." + str(last_num + 1)
            except ValueError:
                # Если не удалось распарсить, просто добавляем .1
                new_code = old_code + ".1"
        else:
            # Для корневых блоков: A2 -> A3
            try:
                num = int(old_code[1:])
                new_code = f"A{num + 1}"
            except ValueError:
                new_code = old_code + "1"
        
        # Проверяем, не конфликтует ли новый код
        conflicting_block = next(
            (b for b in self.blocks 
             if b["model"].code == new_code and b["model"].id != block.id 
             and b["model"].parent_id == block.parent_id),
            None
        )
        
        if conflicting_block:
            # Рекурсивно сдвигаем конфликтующий блок
            self._shift_block_and_children(conflicting_block)
        
        # Обновляем код блока и всех его детей
        self._update_block_code_recursive(block_data, old_code, new_code)
    
    def _update_children_codes_recursive(self, block_data, old_parent_code, new_parent_code):
        """Обновляет коды всех дочерних блоков при изменении кода родителя"""
        children = [b for b in self.blocks if b["model"].parent_id == block_data["model"].id]
        for child_block_data in children:
            child_old_code = child_block_data["model"].code
            # Заменяем префикс кода родителя
            if child_old_code.startswith(old_parent_code + "."):
                child_new_code = child_old_code.replace(old_parent_code + ".", new_parent_code + ".", 1)
                self._update_block_code_recursive(child_block_data, child_old_code, child_new_code)
    
    def show_arrow_action_buttons(self, arrow_data):
        """Показывает кнопки действий для выбранной стрелки."""
        if not hasattr(self, "canvas"):
            return
        
        self.hide_arrow_action_buttons()
        
        arrow = arrow_data["arrow"]
        # Получаем координаты стрелки
        if arrow.display_x1 is None or arrow.display_y1 is None or arrow.display_x2 is None or arrow.display_y2 is None:
            return
        
        # Позиция кнопок - справа от середины стрелки
        mid_x = (arrow.display_x1 + arrow.display_x2) / 2
        mid_y = (arrow.display_y1 + arrow.display_y2) / 2
        base_x = mid_x + 24
        base_y = mid_y
        spacing = 32
        
        buttons_spec = [
            ("copy", "Копировать", "Copy"),
            ("delete", "Удалить", "Close"),
        ]
        
        self.arrow_action_buttons = []
        
        for index, (action, tooltip, icon_name) in enumerate(buttons_spec):
            btn = tk.Button(
                self.canvas,
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                relief="flat",
                bd=0,
                padx=0,
                pady=0,
                activebackground=Colors.SURFACE,
                highlightthickness=0,
                text="",
            )
            self.set_widget_icon(btn, icon_name, (24, 24), compound="center", force_original=True)
            
            if action == "copy":
                btn.configure(command=lambda a=arrow_data: self.copy_arrow(a))
            elif action == "delete":
                btn.configure(command=lambda a=arrow_data: self.delete_arrow_direct(a))
            
            self.apply_hover_effect(btn, enable=False)
            
            y = base_y + (index - 1) * spacing
            win_id = self.canvas.create_window(
                base_x,
                y,
                window=btn,
                anchor="w",
                tags=("arrow_action", f"arrow_actions_{arrow.id}"),
            )
            self.arrow_action_buttons.append({"window_id": win_id, "button": btn, "action": action})
    
    def update_arrow_action_buttons_position(self, arrow_data):
        """Обновляет позицию кнопок действий при перемещении стрелки."""
        if not self.arrow_action_buttons or self.selected_arrow != arrow_data:
            return
        arrow = arrow_data["arrow"]
        if arrow.display_x1 is None or arrow.display_y1 is None or arrow.display_x2 is None or arrow.display_y2 is None:
            return
        mid_x = (arrow.display_x1 + arrow.display_x2) / 2
        mid_y = (arrow.display_y1 + arrow.display_y2) / 2
        base_x = mid_x + 24
        base_y = mid_y
        spacing = 32
        
        for index, data in enumerate(self.arrow_action_buttons):
            y = base_y + (index - 1) * spacing
            try:
                self.canvas.coords(data["window_id"], base_x, y)
            except tk.TclError:
                continue
    
    def hide_arrow_action_buttons(self):
        """Удаляет кнопки действий для стрелки с холста."""
        if not hasattr(self, "canvas"):
            self.arrow_action_buttons = []
            return
        for data in self.arrow_action_buttons:
            try:
                if data.get("window_id"):
                    self.canvas.delete(data["window_id"])
            except tk.TclError:
                pass
            btn = data.get("button")
            if btn is not None and btn.winfo_exists():
                btn.destroy()
        self.arrow_action_buttons = []
    
    def copy_arrow(self, arrow_data):
        """Создаёт копию стрелки рядом с исходной."""
        arrow = arrow_data["arrow"]
        offset = 30
        if arrow.display_x1 is not None and arrow.display_y1 is not None and arrow.display_x2 is not None and arrow.display_y2 is not None:
            new_arrow_data = self.create_arrow_from_point_to_point(
                arrow.display_x1 + offset, arrow.display_y1 + offset,
                arrow.display_x2 + offset, arrow.display_y2 + offset
            )
            # Копируем текст и другие свойства
            if new_arrow_data:
                new_arrow_data["arrow"].text = arrow.text
                new_arrow_data["arrow"].color = arrow.color
                new_arrow_data["arrow"].width = arrow.width
                new_arrow_data["arrow"].style = arrow.style
                self.draw_arrow(new_arrow_data)
    
    def delete_arrow_direct(self, arrow_data):
        """Удаление конкретной стрелки по кнопке."""
        if arrow_data not in self.arrows:
            return
        # Удаляем стрелку (delete_arrow уже удаляет все инструменты)
        self.delete_arrow(arrow_data)
        # Обновляем панель свойств
        if self.selected_arrow == arrow_data:
            self.selected_arrow = None
        self.properties_panel.update_properties(None)
    
    def create_arrow_drag_handles(self, arrow_data):
        """Создаёт маркеры для перетаскивания концов стрелки."""
        self.delete_arrow_drag_handles()
        if not hasattr(self, "canvas"):
            return
        
        arrow = arrow_data["arrow"]
        if arrow.display_x1 is None or arrow.display_y1 is None or arrow.display_x2 is None or arrow.display_y2 is None:
            return
        
        handle_size = 12  # Размер маркеров стрелок (в 1.5 раза больше, чем было)
        
        # Маркер на начале стрелки
        handle_start = self.canvas.create_oval(
            arrow.display_x1 - handle_size, arrow.display_y1 - handle_size,
            arrow.display_x1 + handle_size, arrow.display_y1 + handle_size,
            fill=Colors.PRIMARY,
            outline=Colors.SURFACE,
            width=1,
            tags=("arrow_drag_handle", "arrow_handle_start", arrow.id)
        )
        
        # Маркер на конце стрелки
        handle_end = self.canvas.create_oval(
            arrow.display_x2 - handle_size, arrow.display_y2 - handle_size,
            arrow.display_x2 + handle_size, arrow.display_y2 + handle_size,
            fill=Colors.PRIMARY,
            outline=Colors.SURFACE,
            width=1,
            tags=("arrow_drag_handle", "arrow_handle_end", arrow.id)
        )
        
        self.arrow_drag_handles[arrow.id] = {
            "start": handle_start,
            "end": handle_end,
            "bend": None  # Средний хитбокс для изгиба
        }
        
        # ВАЖНО: Поднимаем маркеры наверх, чтобы они были поверх стрелки и блоков
        self.canvas.tag_raise(handle_start)
        self.canvas.tag_raise(handle_end)
        
        # Привязываем обработчики для перетаскивания
        self.canvas.tag_bind(handle_start, "<ButtonPress-1>", 
                           lambda e, a=arrow_data: self.start_arrow_drag(e, a, "start"))
        self.canvas.tag_bind(handle_start, "<B1-Motion>", 
                           lambda e, a=arrow_data: self.do_arrow_drag(e, a, "start"))
        self.canvas.tag_bind(handle_start, "<ButtonRelease-1>", 
                           lambda e, a=arrow_data: self.end_arrow_drag(e, a))
        
        self.canvas.tag_bind(handle_end, "<ButtonPress-1>", 
                           lambda e, a=arrow_data: self.start_arrow_drag(e, a, "end"))
        self.canvas.tag_bind(handle_end, "<B1-Motion>", 
                           lambda e, a=arrow_data: self.do_arrow_drag(e, a, "end"))
        self.canvas.tag_bind(handle_end, "<ButtonRelease-1>", 
                           lambda e, a=arrow_data: self.end_arrow_drag(e, a))
    
    def delete_arrow_drag_handles(self):
        """Удаляет маркеры перетаскивания стрелки."""
        if not hasattr(self, "canvas"):
            self.arrow_drag_handles = {}
            return
        for handles in self.arrow_drag_handles.values():
            try:
                if handles.get("start"):
                    self.canvas.delete(handles["start"])
                if handles.get("end"):
                    self.canvas.delete(handles["end"])
                if handles.get("bend"):
                    self.canvas.delete(handles["bend"])
            except tk.TclError:
                pass
        self.arrow_drag_handles = {}
    
    def update_arrow_drag_handles(self, arrow_data):
        """Обновляет позицию маркеров при изменении стрелки."""
        if not hasattr(self, "canvas"):
            return
        arrow = arrow_data["arrow"]
        arrow_id = arrow.id
        if arrow_id not in self.arrow_drag_handles:
            return
        if arrow.display_x1 is None or arrow.display_y1 is None or arrow.display_x2 is None or arrow.display_y2 is None:
            return
        
        handles = self.arrow_drag_handles[arrow_id]
        handle_size = 12  # Размер маркеров стрелок (в 1.5 раза больше, чем было)
        
        try:
            self.canvas.coords(handles["start"],
                             arrow.display_x1 - handle_size, arrow.display_y1 - handle_size,
                             arrow.display_x1 + handle_size, arrow.display_y1 + handle_size)
            self.canvas.coords(handles["end"],
                             arrow.display_x2 - handle_size, arrow.display_y2 - handle_size,
                             arrow.display_x2 + handle_size, arrow.display_y2 + handle_size)
        except tk.TclError:
            pass
    
    def start_arrow_drag(self, event, arrow_data, end_type):
        """Начало перетаскивания конца стрелки."""
        if self.current_mode != "select":
            return
        self.dragging_arrow_end = end_type
        arrow = arrow_data["arrow"]
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # ВАЖНО: Сразу открепляем стрелку при начале перетаскивания, если она была прикреплена
        # Это позволяет открепить и двигать стрелку в одно действие
        if end_type == "start":
            # Сохраняем текущие координаты перед откреплением
            if arrow.display_x1 is not None and arrow.display_y1 is not None:
                arrow.x1 = arrow.display_x1
                arrow.y1 = arrow.display_y1
            
            # Открепляем от блока, если был прикреплен
            if arrow.from_block_id:
                arrow.disconnect_from_block(arrow.from_block_id)
            
            # Показываем точки прикрепления для возможности прикрепления к другому блоку
            exclude_block_id = arrow.to_block_id  # Исключаем конечный блок
            self.show_attachment_points(exclude_block_id)
            
            arrow_data["drag_data"] = {
                "start_x": x,
                "start_y": y,
                "orig_x": arrow.display_x1 if arrow.display_x1 is not None else x,
                "orig_y": arrow.display_y1 if arrow.display_y1 is not None else y
            }
        else:
            # Сохраняем текущие координаты перед откреплением
            if arrow.display_x2 is not None and arrow.display_y2 is not None:
                arrow.x2 = arrow.display_x2
                arrow.y2 = arrow.display_y2
            
            # Открепляем от блока, если был прикреплен
            if arrow.to_block_id:
                arrow.disconnect_from_block(arrow.to_block_id)
            
            # Показываем точки прикрепления для возможности прикрепления к другому блоку
            exclude_block_id = arrow.from_block_id  # Исключаем начальный блок
            self.show_attachment_points(exclude_block_id)
            
            arrow_data["drag_data"] = {
                "start_x": x,
                "start_y": y,
                "orig_x": arrow.display_x2 if arrow.display_x2 is not None else x,
                "orig_y": arrow.display_y2 if arrow.display_y2 is not None else y
            }
        
        # Перерисовываем стрелку после открепления
        self.draw_arrow(arrow_data)
        self.update_arrow_drag_handles(arrow_data)
        
        return "break"
    
    def do_arrow_drag(self, event, arrow_data, end_type):
        """Перетаскивание конца стрелки."""
        if self.dragging_arrow_end != end_type or "drag_data" not in arrow_data:
            return
        arrow = arrow_data["arrow"]
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        dx = x - arrow_data["drag_data"]["start_x"]
        dy = y - arrow_data["drag_data"]["start_y"]
        
        # Показываем точки прикрепления при перетаскивании
        if end_type == "start":
            exclude_block_id = arrow.to_block_id  # Исключаем конечный блок
            self.show_attachment_points(exclude_block_id)
        else:
            exclude_block_id = arrow.from_block_id  # Исключаем начальный блок
            self.show_attachment_points(exclude_block_id)
        
        if end_type == "start":
            # Обновляем начальную точку
            # Проверяем, можно ли прикрепить к точке прикрепления
            nearest = self.find_nearest_attachment_point(x, y)
            if nearest:
                # Привязываем к ближайшей точке
                _, _, _, point_x, point_y = nearest
                arrow.display_x1 = point_x
                arrow.display_y1 = point_y
            else:
                # Свободное перемещение
                if arrow.from_block_id is None:
                    # Если стрелка не привязана к блоку, обновляем свободные координаты
                    if arrow.x1 is not None:
                        arrow.x1 = arrow_data["drag_data"]["orig_x"] + dx
                    if arrow.y1 is not None:
                        arrow.y1 = arrow_data["drag_data"]["orig_y"] + dy
                arrow.display_x1 = arrow_data["drag_data"]["orig_x"] + dx
                arrow.display_y1 = arrow_data["drag_data"]["orig_y"] + dy
        else:
            # Обновляем конечную точку
            # Проверяем, можно ли прикрепить к точке прикрепления
            nearest = self.find_nearest_attachment_point(x, y)
            if nearest:
                # Привязываем к ближайшей точке
                _, _, _, point_x, point_y = nearest
                arrow.display_x2 = point_x
                arrow.display_y2 = point_y
            else:
                # Свободное перемещение
                if arrow.to_block_id is None:
                    # Если стрелка не привязана к блоку, обновляем свободные координаты
                    if arrow.x2 is not None:
                        arrow.x2 = arrow_data["drag_data"]["orig_x"] + dx
                    if arrow.y2 is not None:
                        arrow.y2 = arrow_data["drag_data"]["orig_y"] + dy
                arrow.display_x2 = arrow_data["drag_data"]["orig_x"] + dx
                arrow.display_y2 = arrow_data["drag_data"]["orig_y"] + dy
        
        # Перерисовываем стрелку
        self.draw_arrow(arrow_data)
        # Обновляем маркеры и кнопки
        self.update_arrow_drag_handles(arrow_data)
        self.update_arrow_action_buttons_position(arrow_data)
        
        return "break"
    
    def end_arrow_drag(self, event, arrow_data):
        """Завершение перетаскивания конца стрелки."""
        arrow = arrow_data["arrow"]
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Проверяем, можно ли прикрепить к точке прикрепления
        # Используем меньший радиус для более точного прикрепления
        attachment_threshold = 15  # Расстояние для прикрепления (меньше размера маркера)
        
        if self.dragging_arrow_end == "start":
            # Стрелка уже откреплена в start_arrow_drag, просто ищем точку прикрепления
            nearest = self.find_nearest_attachment_point(x, y)
            # Проверяем расстояние до точки прикрепления
            if nearest:
                block_id, side, point_index, point_x, point_y = nearest
                distance = math.sqrt((x - point_x)**2 + (y - point_y)**2)
                # Прикрепляем только если достаточно близко к точке прикрепления
                if distance <= attachment_threshold:
                    arrow.connect_to_block(block_id, side, is_start=True, attachment_point=point_index)
                    arrow.display_x1 = point_x
                    arrow.display_y1 = point_y
                else:
                    # Сохраняем текущие координаты как свободные (открепляем)
                    if arrow.display_x1 is not None and arrow.display_y1 is not None:
                        arrow.x1 = arrow.display_x1
                        arrow.y1 = arrow.display_y1
            else:
                # Сохраняем текущие координаты как свободные
                if arrow.display_x1 is not None and arrow.display_y1 is not None:
                    arrow.x1 = arrow.display_x1
                    arrow.y1 = arrow.display_y1
        elif self.dragging_arrow_end == "end":
            # Стрелка уже откреплена в start_arrow_drag, просто ищем точку прикрепления
            nearest = self.find_nearest_attachment_point(x, y)
            # Проверяем расстояние до точки прикрепления
            if nearest:
                block_id, side, point_index, point_x, point_y = nearest
                distance = math.sqrt((x - point_x)**2 + (y - point_y)**2)
                # Прикрепляем только если достаточно близко к точке прикрепления
                if distance <= attachment_threshold:
                    arrow.connect_to_block(block_id, side, is_start=False, attachment_point=point_index)
                    arrow.display_x2 = point_x
                    arrow.display_y2 = point_y
                else:
                    # Сохраняем текущие координаты как свободные (открепляем)
                    if arrow.display_x2 is not None and arrow.display_y2 is not None:
                        arrow.x2 = arrow.display_x2
                        arrow.y2 = arrow.display_y2
            else:
                # Сохраняем текущие координаты как свободные
                if arrow.display_x2 is not None and arrow.display_y2 is not None:
                    arrow.x2 = arrow.display_x2
                    arrow.y2 = arrow.display_y2
        
        # Скрываем точки прикрепления
        self.hide_attachment_points()
        
        # Перерисовываем стрелку
        self.draw_arrow(arrow_data)
        
        # ВАЖНО: Поднимаем маркеры наверх после отрисовки
        if arrow.id in self.arrow_drag_handles:
            handles = self.arrow_drag_handles[arrow.id]
            if handles.get("start"):
                self.canvas.tag_raise(handles["start"])
            if handles.get("end"):
                self.canvas.tag_raise(handles["end"])
        
        # Обновляем маркеры (позиции)
        self.update_arrow_drag_handles(arrow_data)
        self.update_arrow_action_buttons_position(arrow_data)
        
        if "drag_data" in arrow_data:
            del arrow_data["drag_data"]
        self.dragging_arrow_end = None
        
        # Сохраняем состояние для undo
        self.save_state()
    
    def show_attachment_points(self, exclude_block_id=None):
        """
        Показывает точки прикрепления на всех блоках
        
        Args:
            exclude_block_id: ID блока, на котором не показывать точки (например, блок, от которого начинается стрелка)
        """
        self.hide_attachment_points()
        
        if not hasattr(self, "canvas"):
            return
        
        # Загружаем иконку точки прикрепления
        try:
            icon = self.load_icon("prikrepl", (self.attachment_point_size, self.attachment_point_size), force_original=True)
        except:
            # Если иконка не найдена, используем круг
            icon = None
        
        for block_data in self.blocks:
            if block_data["id"] == exclude_block_id:
                continue
            
            block = block_data["model"]
            
            # Показываем точки на всех сторонах
            for side in ["left", "right", "top", "bottom"]:
                points = block.get_attachment_points(side)
                for point_index, (px, py) in enumerate(points):
                    if icon:
                        # Используем изображение
                        point_id = self.canvas.create_image(
                            px, py,
                            image=icon,
                            tags=("attachment_point", block_data["id"], side, str(point_index))
                        )
                    else:
                        # Используем круг как запасной вариант
                        size = self.attachment_point_size / 2
                        point_id = self.canvas.create_oval(
                            px - size, py - size,
                            px + size, py + size,
                            fill=Colors.PRIMARY,
                            outline=Colors.SURFACE,
                            width=2,
                            tags=("attachment_point", block_data["id"], side, str(point_index))
                        )
                    
                    self.attachment_points.append(point_id)
    
    def update_attachment_points(self):
        """Обновляет позиции всех видимых точек прикрепления"""
        if not hasattr(self, "attachment_points") or not self.attachment_points:
            return
        
        if not hasattr(self, "canvas"):
            return
        
        # Получаем все теги точек прикрепления для обновления
        attachment_data = {}  # {point_id: (block_id, side, point_index, is_image)}
        
        for point_id in self.attachment_points:
            try:
                tags = self.canvas.gettags(point_id)
                if len(tags) >= 4:
                    block_id = tags[1]
                    side = tags[2]
                    point_index = int(tags[3])
                    # Определяем, является ли элемент изображением или овалом
                    item_type = self.canvas.type(point_id)
                    is_image = (item_type == "image")
                    attachment_data[point_id] = (block_id, side, point_index, is_image)
            except (tk.TclError, ValueError, IndexError):
                continue
        
        # Обновляем координаты каждой точки
        for point_id, (block_id, side, point_index, is_image) in attachment_data.items():
            # Находим блок
            block_data = next((b for b in self.blocks if b["id"] == block_id), None)
            if not block_data:
                continue
            
            block = block_data["model"]
            points = block.get_attachment_points(side)
            
            if point_index < len(points):
                px, py = points[point_index]
                try:
                    if is_image:
                        self.canvas.coords(point_id, px, py)
                    else:
                        # Для овала нужно 4 координаты (x1, y1, x2, y2)
                        size = self.attachment_point_size / 2
                        self.canvas.coords(point_id, px - size, py - size, px + size, py + size)
                except tk.TclError:
                    pass
    
    def hide_attachment_points(self):
        """Скрывает все точки прикрепления"""
        if not hasattr(self, "canvas"):
            self.attachment_points = []
            return
        
        for point_id in self.attachment_points:
            try:
                self.canvas.delete(point_id)
            except tk.TclError:
                pass
        self.attachment_points = []
    
    def find_nearest_attachment_point(self, x, y):
        """
        Находит ближайшую точку прикрепления к указанным координатам
        
        Args:
            x, y: Координаты для поиска
            
        Returns:
            tuple или None: (block_id, side, point_index, point_x, point_y) или None
        """
        nearest = None
        min_distance = self.attachment_snap_distance
        
        for block_data in self.blocks:
            block = block_data["model"]
            
            for side in ["left", "right", "top", "bottom"]:
                points = block.get_attachment_points(side)
                for point_index, (px, py) in enumerate(points):
                    distance = math.sqrt((x - px) ** 2 + (y - py) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest = (block_data["id"], side, point_index, px, py)
        
        return nearest

    def set_widget_icon(self, widget, icon_name, size, compound=None, force_original=False, theme_colors=None):
        """
        Назначает иконку виджету и регистрирует связь для автоперерисовки
        при смене темы.
        """
        recolor = None
        if theme_colors:
            theme_key = "dark" if self.is_dark_theme else "light"
            recolor = theme_colors.get(theme_key)
        icon = self.load_icon(icon_name, size, force_original=force_original, recolor=recolor)
        widget.configure(image=icon)
        if compound:
            widget.configure(compound=compound)
        widget.image = icon

        # Запоминаем связь, чтобы можно было обновить иконку после смены темы
        binding = next((b for b in self._icon_bindings if b["widget"] == widget), None)
        data = {
            "widget": widget,
            "icon_name": icon_name,
            "size": size,
            "compound": compound,
            "force_original": force_original,
            "theme_colors": theme_colors,
        }
        if binding:
            binding.update(data)
        else:
            self._icon_bindings.append(data)

    def refresh_icons_for_theme(self):
        """Перезагружает иконки с учётом текущей темы."""
        for binding in list(self._icon_bindings):
            widget = binding["widget"]
            if not widget.winfo_exists():
                continue
            recolor = None
            theme_colors = binding.get("theme_colors")
            if theme_colors:
                theme_key = "dark" if self.is_dark_theme else "light"
                recolor = theme_colors.get(theme_key)
            icon = self.load_icon(
                binding["icon_name"],
                binding["size"],
                force_original=binding.get("force_original", False),
                recolor=recolor,
            )
            widget.configure(image=icon)
            if binding.get("compound"):
                widget.configure(compound=binding["compound"])
            widget.image = icon

    def toggle_theme(self):
        """
        Переключение темы между светлой и тёмной.

        Мы меняем палитру в `Colors`, затем проходим по всем виджетам
        и обновляем их фоны/цвет текста, а также перерисовываем сетку.
        """
        # Определяем исходную и целевую палитру
        if self.is_dark_theme:
            from_palette = Colors.DARK
            Colors.use_light()
            to_palette = Colors.LIGHT
            self.is_dark_theme = False
            print("Переключение на светлую тему")
        else:
            from_palette = Colors.LIGHT
            Colors.use_dark()
            to_palette = Colors.DARK
            self.is_dark_theme = True
            print("Переключение на тёмную тему")

        # Обновляем фон главного окна
        try:
            if self.root.cget("bg") == from_palette["BACKGROUND"]:
                self.root.configure(bg=to_palette["BACKGROUND"])
        except tk.TclError:
            pass

        # Рекурсивно обновляем все виджеты
        self._update_theme_for_widget(self.root, from_palette, to_palette)

        # Применяем цвета к блокам и текстам
        self.apply_theme_to_blocks(from_palette, to_palette)
        
        # Применяем цвета к стрелкам
        self.apply_theme_to_arrows(from_palette, to_palette)

        # Перерисовываем иконки
        self.refresh_icons_for_theme()

        # Перерисовываем сетку с новыми цветами
        # Сетка всегда рисуется с одинаковыми размерами независимо от темы
        if hasattr(self, "canvas"):
            self.draw_grid()

        self.update_theme_button_label()
        
        # Пересоздаем меню настроек, если оно открыто, чтобы применить новую тему
        if hasattr(self, 'settings_menu') and self.settings_menu and self.settings_menu.winfo_exists():
            try:
                # Проверяем, видимо ли меню
                grid_info = self.settings_menu.grid_info()
                if grid_info:
                    # Удаляем старую кнопку закрытия, если она есть
                    for widget in self.settings_menu.winfo_children():
                        if isinstance(widget, tk.Button) and widget.winfo_exists():
                            try:
                                widget_text = widget.cget("text")
                                if widget_text == "✕":
                                    widget.destroy()
                            except:
                                pass
                    # Пересоздаем меню с новыми цветами темы
                    self.create_settings_menu()
            except:
                pass

    def update_theme_button_label(self):
        """Обновляет подпись кнопки переключения темы."""
        if not hasattr(self, "theme_toggle_btn"):
            return
        text = "Светлая тема" if self.is_dark_theme else "Тёмная тема"
        self.theme_toggle_btn.config(text=text)

    def apply_theme_to_blocks(self, from_palette, to_palette):
        """Обновляет цвета блоков и текста на canvas при смене темы."""
        if not hasattr(self, "canvas"):
            return

        from_fill = (from_palette.get("BLOCK_FILL") or "").lower()
        from_border = (from_palette.get("BLOCK_BORDER") or "").lower()
        new_fill = to_palette.get("BLOCK_FILL", Colors.BLOCK_FILL)
        new_border = to_palette.get("BLOCK_BORDER", Colors.BLOCK_BORDER)
        new_text = to_palette.get("TEXT_PRIMARY", Colors.TEXT_PRIMARY)

        for block_data in self.blocks:
            rect_id = block_data["rect_id"]
            text_id = block_data["text_id"]

            current_fill = self.canvas.itemcget(rect_id, "fill").lower()
            if current_fill == from_fill:
                self.canvas.itemconfig(rect_id, fill=new_fill)
                block_data["model"].color = new_fill

            current_outline = self.canvas.itemcget(rect_id, "outline").lower()
            if self.selected_block == block_data:
                self.canvas.itemconfig(rect_id, outline=Colors.PRIMARY, width=3)
                # Пересоздаем маркеры resize, чтобы цвета соответствовали теме
                self.delete_resize_handles(block_data)
                self.create_resize_handles(block_data)
            else:
                if current_outline == from_border:
                    self.canvas.itemconfig(rect_id, outline=new_border,
                                           width=block_data["model"].border_width)

            # Обновляем цвет текста блока
            self.canvas.itemconfig(text_id, fill=new_text)
    
    def apply_theme_to_arrows(self, from_palette, to_palette):
        """Обновляет цвета стрелок при смене темы."""
        if not hasattr(self, "canvas"):
            return
        
        new_arrow_color = to_palette.get("ARROW_COLOR", Colors.ARROW_COLOR)
        
        for arrow_data in self.arrows:
            arrow = arrow_data["arrow"]
            # Обновляем цвет стрелки на цвет из темы
            arrow.color = new_arrow_color
            
            # Перерисовываем стрелку с новым цветом
            if arrow_data.get("line_id") or arrow_data.get("arrowhead_id"):
                self.draw_arrow(arrow_data)

    def _update_theme_for_widget(self, widget, from_palette, to_palette):
        """
        Рекурсивно обновляет цвета виджета и всех его потомков.

        Подход простой: если текущий bg/fg совпадает с цветом старой темы,
        заменяем его на соответствующий цвет новой темы.
        """
        # Фон
        for key in ("BACKGROUND", "SURFACE", "SIDEBAR", "HOVER"):
            try:
                current_bg = widget.cget("bg")
            except tk.TclError:
                current_bg = None
            if current_bg == from_palette.get(key):
                try:
                    widget.configure(bg=to_palette.get(key))
                except tk.TclError:
                    pass

        # Цвет текста
        for key in ("TEXT_PRIMARY", "TEXT_SECONDARY"):
            try:
                current_fg = widget.cget("fg")
            except tk.TclError:
                current_fg = None
            if current_fg == from_palette.get(key):
                try:
                    widget.configure(fg=to_palette.get(key))
                except tk.TclError:
                    pass

        # Границы/обводка/активный фон — по возможности тоже обновляем
        try:
            hb = widget.cget("highlightbackground")
            if hb == from_palette.get("BORDER"):
                widget.configure(highlightbackground=to_palette.get("BORDER"))
        except tk.TclError:
            pass

        try:
            ab = widget.cget("activebackground")
            for key in ("SURFACE", "HOVER", "ACTIVE"):
                if ab == from_palette.get(key):
                    widget.configure(activebackground=to_palette.get(key))
                    break
        except tk.TclError:
            pass

        try:
            ib = widget.cget("insertbackground")
            if ib == from_palette.get("TEXT_PRIMARY"):
                widget.configure(insertbackground=to_palette.get("TEXT_PRIMARY"))
        except tk.TclError:
            pass

        # Рекурсивно обрабатываем детей
        for child in widget.winfo_children():
            self._update_theme_for_widget(child, from_palette, to_palette)

    def on_ctrl_mousewheel(self, event):
        """Масштабирование при Ctrl + колесо мыши с центрированием на курсоре"""
        # На Windows delta кратна 120
        delta = 1 if event.delta > 0 else -1
        factor = 1.1 if delta > 0 else 0.9
        self.apply_zoom(factor, anchor_screen=(event.x, event.y))

    def on_ctrl_scroll_steps(self, steps):
        """Fallback для систем, где колесо приходит как Button-4/5"""
        factor = 1.1 if steps > 0 else 0.9
        # Центр по текущему положению курсора относительно canvas
        try:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        except Exception:
            x, y = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
        self.apply_zoom(factor, anchor_screen=(x, y))

    def apply_zoom(self, factor, anchor_screen=None):
        """Применяет масштабирование ко всем элементам canvas"""
        # Ограничиваем общий масштаб
        new_scale = self.zoom_scale * factor
        new_scale = max(0.2, min(4.0, new_scale))
        # Нормализуем фактор если достигли границ
        if abs(new_scale - self.zoom_scale) < 1e-6:
            return
        norm_factor = new_scale / self.zoom_scale

        # Точка якоря в координатах canvas
        if anchor_screen is None:
            cx = self.canvas.canvasx(self.canvas.winfo_width() // 2)
            cy = self.canvas.canvasy(self.canvas.winfo_height() // 2)
        else:
            sx, sy = anchor_screen
            cx = self.canvas.canvasx(sx)
            cy = self.canvas.canvasy(sy)

        # Масштабируем все элементы, включая сетку
        self.canvas.scale("all", cx, cy, norm_factor, norm_factor)

        # Перерисовываем/обновляем элементы, чувствительные к масштабу
        # Текст в Tk не масштабируется шрифтом — оставляем как есть для простоты

        # Пересчёт границ прокрутки по содержимому
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

        # Обновляем текущий масштаб и UI
        self.zoom_scale = new_scale
        percent = int(round(self.zoom_scale * 100))
        if hasattr(self, "zoom_label"):
            self.zoom_label.config(text=f"{percent}%")
        if hasattr(self, "footer_label"):
            base = "Диаграмма: Пример IDEF0 | Масштаб: "
            self.footer_label.config(text=f"{base}{percent}%")

    def on_space_press(self, event):
        """Обработчик нажатия пробела - временное включение панорамирования"""
        if self.current_mode == "select":
            self.canvas.configure(cursor="hand2")
            self.is_panning = True

    def on_space_release(self, event):
        """Обработчик отпускания пробела - возврат к предыдущему режиму"""
        if self.current_mode == "select":
            self.canvas.configure(cursor="")
            self.is_panning = False

    def on_canvas_click(self, event):
        """Обработчик клика по холсту"""
        if self.is_panning:
            # Если включено панорамирование (пробел зажат), начинаем панорамирование
            self.canvas.scan_mark(event.x, event.y)
        elif self.current_mode == "draw_arrow":
            # В режиме рисования стрелок - начинаем рисование стрелки
            # Преобразуем координаты мыши в координаты холста
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Проверяем, кликнули ли по блоку
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            block_clicked = None
            for item in items:
                tags = self.canvas.gettags(item)
                if "block" in tags:
                    # Находим блок по тегу
                    for tag in tags:
                        if tag.startswith("block_"):
                            block_clicked = next((b for b in self.blocks if b["id"] == tag), None)
                            break
                    if block_clicked:
                        break
            
            if block_clicked:
                # Начинаем стрелку от блока
                self.arrow_start_block = block_clicked
                self.arrow_start_x = None
                self.arrow_start_y = None
                print(f"Начало стрелки от блока: {block_clicked['id']}")
            else:
                # Начинаем стрелку от точки на холсте
                self.arrow_start_block = None
                self.arrow_start_x = x
                self.arrow_start_y = y
                print(f"Начало стрелки от точки: ({x:.1f}, {y:.1f})")
            
            self.arrow_drawing = True
        else:
            # Если не панорамирование, проверяем клик по блоку или маркеру
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            block_or_handle_clicked = False
            arrow_clicked = False
            for item in items:
                tags = self.canvas.gettags(item)
                if "block" in tags or "resize_handle" in tags:
                    block_or_handle_clicked = True
                    break
                if "arrow_line" in tags or "arrow_hitbox" in tags or "arrow_arrowhead" in tags:
                    arrow_clicked = True
                    # Находим стрелку по тегу
                    arrow_id = None
                    for tag in tags:
                        if tag.startswith("arrow_"):
                            arrow_id = tag
                            break
                    if arrow_id:
                        arrow_data = next((a for a in self.arrows if a["arrow"].id == arrow_id), None)
                        if arrow_data:
                            self.select_arrow(arrow_data)
                    break
            
            # Если клик был не по блоку, маркеру или стрелке - сбрасываем выделение
            if not block_or_handle_clicked and not arrow_clicked:
                if self.selected_block:
                    prev_model = self.selected_block["model"]
                    self.canvas.itemconfig(
                        self.selected_block["rect_id"],
                        outline=Colors.BLOCK_BORDER,
                        width=prev_model.border_width
                    )
                    self.delete_resize_handles(self.selected_block)
                    self.selected_block = None
                    self.hide_block_action_buttons()
                if self.selected_arrow:
                    self.deselect_arrow()
                    self.properties_panel.update_properties(None)
                    print("Сброс выделения")

    def on_canvas_release(self, event):
        """Обработчик отпускания кнопки мыши на холсте"""
        # Сбрасываем перетаскиваемый блок
        self.dragging_block = None
        # Сбрасываем изменение размера
        self.resizing_block = None
        
        # Завершаем рисование стрелки
        if self.current_mode == "draw_arrow" and self.arrow_drawing:
            # Преобразуем координаты мыши в координаты холста
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Проверяем, отпустили ли на блоке
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            end_block = None
            for item in items:
                tags = self.canvas.gettags(item)
                if "block" in tags:
                    # Находим блок по тегу
                    for tag in tags:
                        if tag.startswith("block_"):
                            end_block = next((b for b in self.blocks if b["id"] == tag), None)
                            break
                    if end_block:
                        break
            
            # Удаляем превью
            if self.arrow_preview_line:
                self.canvas.delete(self.arrow_preview_line)
                self.arrow_preview_line = None
            
            # Создаем стрелку
            if self.arrow_start_block and end_block:
                # Стрелка от блока к блоку
                if self.arrow_start_block["id"] != end_block["id"]:
                    from_side, to_side = self._determine_arrow_sides(
                        self.arrow_start_block["model"],
                        end_block["model"]
                    )
                    self.create_arrow_between_blocks(
                        self.arrow_start_block["id"],
                        end_block["id"],
                        from_side=from_side,
                        to_side=to_side
                    )
            elif self.arrow_start_block:
                # Стрелка от блока к точке
                self.create_arrow_from_block_to_point(
                    self.arrow_start_block["id"],
                    x, y
                )
            elif end_block:
                # Стрелка от точки к блоку
                self.create_arrow_from_point_to_block(
                    self.arrow_start_x, self.arrow_start_y,
                    end_block["id"]
                )
            elif self.arrow_start_x is not None and self.arrow_start_y is not None:
                # Стрелка от точки к точке
                self.create_arrow_from_point_to_point(
                    self.arrow_start_x, self.arrow_start_y,
                    x, y
                )
            
            # Сбрасываем состояние
            self.arrow_start_block = None
            self.arrow_start_x = None
            self.arrow_start_y = None
            self.arrow_drawing = False
            
            # Сохраняем состояние для undo
            self.save_state()
            
            # Переключаем режим на начальный (select) после создания стрелки
            self.enable_select_mode()

    def on_canvas_drag(self, event):
        """Обработчик перетаскивания мыши на холсте"""
        if self.is_panning:
            # Панорамирование
            self.canvas.scan_dragto(event.x, event.y, gain=1)
        elif self.current_mode == "draw_arrow" and self.arrow_drawing:
            # Рисование стрелки - обновляем превью
            self.on_canvas_motion(event)
    
    def on_canvas_motion(self, event):
        """Обработчик движения мыши для превью стрелки"""
        if self.current_mode == "draw_arrow" and self.arrow_drawing:
            # Преобразуем координаты мыши в координаты холста
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Определяем начальную точку
            start_x = None
            start_y = None
            
            if self.arrow_start_block:
                # Начало от блока
                start_block = self.arrow_start_block["model"]
                # Определяем сторону начального блока на основе направления к курсору
                dx = x - start_block.x
                dy = y - start_block.y
                
                if abs(dx) > abs(dy):
                    from_side = "right" if dx > 0 else "left"
                else:
                    from_side = "bottom" if dy > 0 else "top"
                
                start_x, start_y = self._get_block_side_point(start_block, from_side)
            elif self.arrow_start_x is not None and self.arrow_start_y is not None:
                # Начало от точки
                start_x = self.arrow_start_x
                start_y = self.arrow_start_y
            
            if start_x is not None and start_y is not None:
                # Удаляем старый превью
                if self.arrow_preview_line:
                    self.canvas.delete(self.arrow_preview_line)
                
                # Создаем новый превью
                self.arrow_preview_line = self.canvas.create_line(
                    start_x, start_y, x, y,
                    fill=Colors.PRIMARY,
                    width=2,
                    dash=(4, 2),
                    tags="arrow_preview"
                )
    
    def handle_arrow_click(self, block_data):
        """Обработчик клика по блоку в режиме рисования стрелок"""
        print(f"handle_arrow_click вызван для блока {block_data['id']}, arrow_start_block={self.arrow_start_block}")
        if not self.arrow_start_block:
            # Устанавливаем начальный блок
            self.arrow_start_block = block_data
            print(f"Выбран начальный блок для стрелки: {block_data['id']}")
        else:
            # Создаем стрелку от начального блока к текущему
            if self.arrow_start_block["id"] != block_data["id"]:
                # Определяем стороны для соединения
                from_side, to_side = self._determine_arrow_sides(
                    self.arrow_start_block["model"],
                    block_data["model"]
                )
                
                print(f"Создание стрелки: от {self.arrow_start_block['id']} ({from_side}) к {block_data['id']} ({to_side})")
                
                # Создаем стрелку
                arrow_data = self.create_arrow_between_blocks(
                    self.arrow_start_block["id"],
                    block_data["id"],
                    from_side=from_side,
                    to_side=to_side
                )
                
                print(f"Стрелка создана: {arrow_data['arrow'].id}")
                
                # Сбрасываем режим рисования
                self.arrow_start_block = None
                if self.arrow_preview_line:
                    self.canvas.delete(self.arrow_preview_line)
                    self.arrow_preview_line = None
            else:
                # Клик по тому же блоку - сбрасываем выбор
                self.arrow_start_block = None
                if self.arrow_preview_line:
                    self.canvas.delete(self.arrow_preview_line)
                    self.arrow_preview_line = None
                print("Сброс начального блока (клик по тому же блоку)")
    
    def _determine_arrow_sides(self, from_block, to_block):
        """
        Определяет стороны блоков для соединения стрелкой
        
        Args:
            from_block: Модель начального блока
            to_block: Модель конечного блока
            
        Returns:
            tuple: (from_side, to_side) - стороны для соединения
        """
        # Вычисляем вектор от начального блока к конечному
        dx = to_block.x - from_block.x
        dy = to_block.y - from_block.y
        
        # Определяем сторону начального блока (откуда выходит стрелка)
        if abs(dx) > abs(dy):
            # Горизонтальное направление
            from_side = "right" if dx > 0 else "left"
        else:
            # Вертикальное направление
            from_side = "bottom" if dy > 0 else "top"
        
        # Определяем сторону конечного блока (куда входит стрелка)
        if abs(dx) > abs(dy):
            # Горизонтальное направление
            to_side = "left" if dx > 0 else "right"
        else:
            # Вертикальное направление
            to_side = "top" if dy > 0 else "bottom"
        
        return from_side, to_side
    
    def _get_block_side_point(self, block, side):
        """
        Получает точку на стороне блока (вспомогательный метод)
        
        Args:
            block: Модель блока
            side: Сторона ("left", "right", "top", "bottom")
            
        Returns:
            tuple: (x, y) координаты точки
        """
        x = block.x
        y = block.y
        width = block.width
        height = block.height
        
        if side == "left":
            return (x - width / 2, y)
        elif side == "right":
            return (x + width / 2, y)
        elif side == "top":
            return (x, y - height / 2)
        elif side == "bottom":
            return (x, y + height / 2)
        else:
            return (x, y)

    def apply_hover_effect(self, widget, base_attr="SURFACE", enable=True):
        """Ховер-эффект с учетом текущей темы.

        Для «чистых» иконок без фона можно передать enable=False.
        """
        if not enable:
            return

        def on_enter(_):
            try:
                widget.configure(bg=Colors.HOVER)
            except tk.TclError:
                pass

        def on_leave(_):
            base_color = getattr(Colors, base_attr, Colors.SURFACE)
            try:
                widget.configure(bg=base_color)
            except tk.TclError:
                pass

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def draw_grid(self):
        """Рисует сетку по всей области холста"""
        self.canvas.delete('grid')
        
        # Рисуем сетку на всей области scrollregion
        left, top, right, bottom = self.canvas.cget('scrollregion').split()
        left, top, right, bottom = int(left), int(top), int(right), int(bottom)

        # Используем константы для размеров сетки (одинаковые для всех тем)
        minor_step = Dimensions.GRID_MINOR_STEP
        major_step = Dimensions.GRID_MAJOR_STEP

        # Minor grid - более светлая
        for i in range(left, right, minor_step):
            self.canvas.create_line(i, top, i, bottom, fill=Colors.GRID, width=1, tags='grid')
        for i in range(top, bottom, minor_step):
            self.canvas.create_line(left, i, right, i, fill=Colors.GRID, width=1, tags='grid')

        # Major grid - немного темнее
        for i in range(left, right, major_step):
            self.canvas.create_line(i, top, i, bottom, fill=Colors.GRID_STRONG, width=1, tags='grid')
        for i in range(top, bottom, major_step):
            self.canvas.create_line(left, i, right, i, fill=Colors.GRID_STRONG, width=1, tags='grid')

        # Отправляем сетку под все элементы, чтобы она не перекрывала объекты
        try:
            self.canvas.tag_lower('grid')
        except tk.TclError:
            pass

    def _ensure_grid_at_bottom(self):
        """Гарантируем, что сетка остаётся под всеми элементами."""
        if hasattr(self, "canvas"):
            try:
                self.canvas.tag_lower('grid')
            except tk.TclError:
                pass

    def bring_selected_forward(self):
        """Поднимает выбранный элемент (блок или стрелку) на передний план."""
        if self.selected_block:
            self._raise_block(self.selected_block)
            print(f"Блок {self.selected_block['id']} поднят на передний план")
        elif self.selected_arrow:
            self._raise_arrow(self.selected_arrow)
            print(f"Стрелка {self.selected_arrow['arrow'].id} поднята на передний план")
        else:
            print("Выберите блок или стрелку для изменения порядка слоев")

    def send_selected_backward(self):
        """Опускает выбранный элемент (блок или стрелку) на задний план (но над сеткой)."""
        if self.selected_block:
            self._lower_block(self.selected_block)
            print(f"Блок {self.selected_block['id']} опущен на задний план")
        elif self.selected_arrow:
            self._lower_arrow(self.selected_arrow)
            print(f"Стрелка {self.selected_arrow['arrow'].id} опущена на задний план")
        else:
            print("Выберите блок или стрелку для изменения порядка слоев")
        self._ensure_grid_at_bottom()

    def _raise_block(self, block_data):
        """Поднимает указанный блок и связанные элементы."""
        if not block_data:
            return
        
        block_id = block_data.get("id")
        if not block_id:
            return
        
        try:
            # Поднимаем все элементы блока по тегу (более надежный способ)
            self.canvas.tag_raise(block_id)
            
            # Также поднимаем отдельные элементы для надежности
            if block_data.get("rect_id"):
                self.canvas.tag_raise(block_data["rect_id"])
            if block_data.get("text_id"):
                self.canvas.tag_raise(block_data["text_id"])
            if block_data.get("code_text_id"):
                self.canvas.tag_raise(block_data["code_text_id"])
            
            # Поднимаем маркеры изменения размера
            for handle_id in block_data.get("resize_handles", {}).values():
                try:
                    self.canvas.tag_raise(handle_id)
                except tk.TclError:
                    pass
        except tk.TclError:
            pass
        except (KeyError, AttributeError):
            pass

        # Поднимаем кнопки действий, если блок выбран
        if self.selected_block == block_data:
            for btn_data in self.block_action_buttons:
                try:
                    if btn_data.get("window_id"):
                        self.canvas.tag_raise(btn_data["window_id"])
                except tk.TclError:
                    pass

    def _lower_block(self, block_data):
        """Опускает указанный блок и связанные элементы."""
        if not block_data:
            return
        
        block_id = block_data.get("id")
        if not block_id:
            return
        
        try:
            # Опускаем все элементы блока по тегу (более надежный способ)
            self.canvas.tag_lower(block_id)
            
            # Также опускаем отдельные элементы для надежности
            if block_data.get("rect_id"):
                self.canvas.tag_lower(block_data["rect_id"])
            if block_data.get("text_id"):
                self.canvas.tag_lower(block_data["text_id"])
            if block_data.get("code_text_id"):
                self.canvas.tag_lower(block_data["code_text_id"])
            
            # Опускаем маркеры изменения размера
            for handle_id in block_data.get("resize_handles", {}).values():
                try:
                    self.canvas.tag_lower(handle_id)
                except tk.TclError:
                    pass
        except tk.TclError:
            pass
        except (KeyError, AttributeError):
            pass

        # Опускаем кнопки действий, если блок выбран
        if self.selected_block == block_data:
            for btn_data in self.block_action_buttons:
                try:
                    if btn_data.get("window_id"):
                        self.canvas.tag_lower(btn_data["window_id"])
                except tk.TclError:
                    pass
        
        # Убеждаемся, что сетка остается внизу
        self._ensure_grid_at_bottom()

    def _raise_arrow(self, arrow_data):
        """Поднимает стрелку и её вспомогательные элементы."""
        if not arrow_data or "arrow" not in arrow_data:
            return
        
        try:
            if arrow_data.get("line_id"):
                self.canvas.tag_raise(arrow_data["line_id"])
            if arrow_data.get("arrowhead_id"):
                self.canvas.tag_raise(arrow_data["arrowhead_id"])
            if arrow_data.get("hitbox_id"):
                self.canvas.tag_raise(arrow_data["hitbox_id"])
            if arrow_data.get("text_id"):
                self.canvas.tag_raise(arrow_data["text_id"])
            if arrow_data.get("text_outline_ids"):
                for outline_id in arrow_data["text_outline_ids"]:
                    try:
                        self.canvas.tag_raise(outline_id)
                    except tk.TclError:
                        pass
        except tk.TclError:
            pass
        except (KeyError, AttributeError):
            pass

        try:
            handles = self.arrow_drag_handles.get(arrow_data["arrow"].id)
            if handles:
                for handle_id in handles.values():
                    try:
                        self.canvas.tag_raise(handle_id)
                    except tk.TclError:
                        pass
        except (KeyError, AttributeError):
            pass

        if self.selected_arrow == arrow_data:
            for btn_data in self.arrow_action_buttons:
                try:
                    if btn_data.get("window_id"):
                        self.canvas.tag_raise(btn_data["window_id"])
                except tk.TclError:
                    pass

    def _lower_arrow(self, arrow_data):
        """Опускает стрелку и её вспомогательные элементы."""
        if not arrow_data or "arrow" not in arrow_data:
            return
        
        try:
            if arrow_data.get("line_id"):
                self.canvas.tag_lower(arrow_data["line_id"])
            if arrow_data.get("arrowhead_id"):
                self.canvas.tag_lower(arrow_data["arrowhead_id"])
            if arrow_data.get("hitbox_id"):
                self.canvas.tag_lower(arrow_data["hitbox_id"])
            if arrow_data.get("text_id"):
                self.canvas.tag_lower(arrow_data["text_id"])
            if arrow_data.get("text_outline_ids"):
                for outline_id in arrow_data["text_outline_ids"]:
                    try:
                        self.canvas.tag_lower(outline_id)
                    except tk.TclError:
                        pass
        except tk.TclError:
            pass
        except (KeyError, AttributeError):
            pass

        try:
            handles = self.arrow_drag_handles.get(arrow_data["arrow"].id)
            if handles:
                for handle_id in handles.values():
                    try:
                        self.canvas.tag_lower(handle_id)
                    except tk.TclError:
                        pass
        except (KeyError, AttributeError):
            pass

        if self.selected_arrow == arrow_data:
            for btn_data in self.arrow_action_buttons:
                try:
                    if btn_data.get("window_id"):
                        self.canvas.tag_lower(btn_data["window_id"])
                except tk.TclError:
                    pass
        
        # Убеждаемся, что сетка остается внизу
        self._ensure_grid_at_bottom()

    def setup_layers_panel(self, parent):
        """Создает панель слоев"""
        # Основной контейнер для панели слоев
        self.layers_panel_frame = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            width=Dimensions.PROPERTIES_WIDTH,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        self.layers_panel_frame.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        self.layers_panel_frame.grid_remove()  # Скрываем initially
        self.layers_panel_frame.pack_propagate(False)

        # Заголовок панели слоев
        header_frame = tk.Frame(self.layers_panel_frame, bg=Colors.SURFACE, height=40)
        header_frame.pack(fill=tk.X, padx=16, pady=8)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Слои диаграммы",
            font=Fonts.SECTION,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY
        )
        title_label.pack(side=tk.LEFT)

        close_btn = tk.Button(
            header_frame,
            text="×",
            font=("Segoe UI", 16, "bold"),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            relief="flat",
            bd=0,
            command=self.show_properties_panel
        )
        close_btn.pack(side=tk.RIGHT)
        self.apply_hover_effect(close_btn, base_attr="SURFACE")

        # Контейнер для дерева слоев
        tree_frame = tk.Frame(self.layers_panel_frame, bg=Colors.SURFACE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Создаем Treeview для иерархии
        self.layers_tree = ttk.Treeview(
            tree_frame,
            columns=("code",),
            show="tree",
            selectmode="browse"
        )

        # Стилизация Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                    background=Colors.SURFACE,
                    fieldbackground=Colors.SURFACE,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.BODY)
        style.configure("Treeview.Heading",
                    background=Colors.SURFACE,
                    foreground=Colors.TEXT_PRIMARY)
        style.map("Treeview", background=[('selected', Colors.PRIMARY)])

        # Scrollbar для дерева
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.layers_tree.yview)
        self.layers_tree.configure(yscrollcommand=tree_scroll.set)

        # Размещаем дерево и скроллбар
        self.layers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязываем обработчик двойного клика
        self.layers_tree.bind("<Double-1>", self.on_layer_double_click)

    def toggle_layers_panel(self):
        """Переключает между панелью свойств и панелью слоев"""
        if self.current_right_panel == "properties":
            self.show_layers_panel()
        else:
            self.show_properties_panel()

    def show_layers_panel(self):
        """Показывает панель слоев вместо панели свойств"""
        # Скрываем свойства
        self.properties_panel.grid_remove()
        
        # Показываем слои
        self.layers_panel_frame.grid()
        self.update_layers_tree()
        
        self.current_right_panel = "layers"
        self.layers_panel_visible = True
        print("Панель слоев открыта")

    def show_properties_panel(self):
        """Показывает панель свойств вместо слоев"""
        # Скрываем слои
        self.layers_panel_frame.grid_remove()
        
        # Показываем свойства
        self.properties_panel.grid()
        
        self.current_right_panel = "properties"
        self.layers_panel_visible = False
        print("Панель свойств открыта")

    def update_layers_tree(self):
        """Обновляет дерево слоев"""
        # Очищаем текущее дерево
        for item in self.layers_tree.get_children():
            self.layers_tree.delete(item)

        # Строим иерархию
        hierarchy = self.layer_manager.build_hierarchy_tree([b["model"] for b in self.blocks])
        
        # Добавляем корневой уровень
        root_item = self.layers_tree.insert("", "end", text="Корневой уровень", 
                                        values=("",), tags=("root",))
        
        # Рекурсивно добавляем дочерние элементы
        self.add_children_to_tree(root_item, hierarchy)
        
        # Раскрываем все уровни
        def expand_all(parent=""):
            for child in self.layers_tree.get_children(parent):
                self.layers_tree.item(child, open=True)
                expand_all(child)
        
        expand_all()
        
    def add_children_to_tree(self, parent_item, children):
        """Рекурсивно добавляет дочерние элементы в дерево"""
        for child_data in children:
            block = child_data['block']
            
            # Отображаем код блока
            item_text = f"{block.code}"
            
            child_item = self.layers_tree.insert(
                parent_item, "end", 
                text=item_text,
                values=(block.id,),
                tags=("block",)
            )
            
            # Рекурсивно добавляем детей
            if child_data['children']:
                self.add_children_to_tree(child_item, child_data['children'])

    def on_layer_double_click(self, event):
        """Обработчик двойного клика по элементу дерева слоев"""
        item = self.layers_tree.selection()[0] if self.layers_tree.selection() else None
        if item:
            tags = self.layers_tree.item(item, "tags")
            values = self.layers_tree.item(item, "values")
            
            if "block" in tags and values:
                block_id = values[0]
                block_code = self.layers_tree.item(item, "text")
                
                print(f"Двойной клик на блоке {block_code} (id: {block_id})")
                
                # Переходим на уровень блока
                self.navigate_to_block_level(block_id)
                
                # Ждем обновления интерфейса
                self.root.update()
                
                # Находим блок по ID модели
                for block_data in self.blocks:
                    if block_data["model"].id == block_id:
                        print(f"Найден блок: {block_data['model'].code}, выделяем...")
                        self.select_block(block_data)
                        break
                else:
                    print(f"Блок с id {block_id} не найден в списке блоков")

    def navigate_to_block_level(self, block_id):
        """Переходит на уровень указанного блока"""
        # Находим блок
        block_data = next((b for b in self.blocks if b["model"].id == block_id), None)
        if block_data:
            path = self.build_path_to_block(block_id)  
            
            # Сохраняем текущее состояние
            current_level_key = self.layer_manager.get_current_level_key()
            self.save_current_level_state(current_level_key)
            
            # Переходим на новый уровень
            self.layer_manager.goto_level_path(path)
            
            # Восстанавливаем состояние
            new_level_key = self.layer_manager.get_current_level_key()
            self.restore_level_state(new_level_key)
            
            self.update_footer_info()
            print(f"Перешли на уровень блока {block_data['model'].code}")

    def build_path_to_block(self, target_block_id):
        """Строит путь до указанного блока"""
        def find_path(current_block_id, path):
            if current_block_id == target_block_id:
                return path + [current_block_id]
            
            # Ищем детей текущего блока
            child_blocks = [b for b in self.blocks if b["model"].parent_id == current_block_id]
            
            for child_block in child_blocks:
                result = find_path(child_block["model"].id, path + [current_block_id])
                if result:
                    return result
            
            return None
        
        # Начинаем с корневого уровня
        root_blocks = [b for b in self.blocks if b["model"].parent_id is None]
        for root_block in root_blocks:
            result = find_path(root_block["model"].id, [])
            if result:
                return result[:-1]  # Возвращаем путь без самого блока (только родители)
        
        return []

    def save_current_level_state(self, level_key):
        """Сохраняет состояние текущего уровня"""
        # Получаем текущую позицию прокрутки
        x_view = self.canvas.xview()[0]
        y_view = self.canvas.yview()[0]
        
        state = {
            'x_view': x_view,
            'y_view': y_view,
            'selected_block_id': self.selected_block["id"] if self.selected_block else None
        }
        
        self.layer_manager.save_level_state(level_key, state)

    def restore_level_state(self, level_key):
        """Восстанавливает состояние уровня"""
        # Обновляем холст
        self.refresh_canvas()
        
        # Восстанавливаем позицию прокрутки если есть сохраненное состояние
        state = self.layer_manager.get_level_state(level_key)
        if state:
            self.canvas.xview_moveto(state['x_view'])
            self.canvas.yview_moveto(state['y_view'])
            
            # Восстанавливаем выделение блока если есть
            if state['selected_block_id']:
                block_data = next((b for b in self.blocks if b["id"] == state['selected_block_id']), None)
                if block_data:
                    self.select_block(block_data)
        else:
            # Если состояния нет, устанавливаем вид по умолчанию
            self.canvas.xview_moveto(0.5)
            self.canvas.yview_moveto(0.5)

    def refresh_canvas(self):
        """Обновляет холст в соответствии с текущим уровнем"""
        # Очищаем холст
        self.canvas.delete("all")
        
        # Перерисовываем сетку
        self.draw_grid()
        
        # Получаем блоки для текущего уровня
        current_blocks_models = self.layer_manager.get_blocks_for_current_level([b["model"] for b in self.blocks])
        current_blocks_ids = [block.id for block in current_blocks_models]
        
        # Перерисовываем только блоки текущего уровня
        for block_data in self.blocks:
            if block_data["model"].id in current_blocks_ids:
                self.redraw_block(block_data)
        
        # Перерисовываем стрелки, которые связаны с видимыми блоками
        self.draw_all_arrows()
        
        # Сбрасываем выделение только если выбранный блок не принадлежит текущему уровню
        if self.selected_block and self.selected_block["model"].id not in current_blocks_ids:
            self.selected_block = None
            self.properties_panel.update_properties(None)
            print("Сброс выделения: блок не принадлежит текущему уровню")

    def redraw_block(self, block_data):
        """Перерисовывает блок на холсте"""
        model = block_data["model"]
        
        # Рисуем прямоугольник
        rect = self.canvas.create_rectangle(
            model.x - model.width / 2, model.y - model.height / 2,
            model.x + model.width / 2, model.y + model.height / 2,
            fill=model.color,
            outline=Colors.BLOCK_BORDER,
            width=model.border_width,
            tags=("block", block_data["id"])
        )

        # Добавляем основной текст
        formatted_text = self.format_block_text(model.name, model.width)
        text = self.canvas.create_text(
            model.x, model.y,
            text=formatted_text,
            font=("Segoe UI", 10),
            fill=Colors.TEXT_PRIMARY,
            justify="center",
            width=model.width - 10,
            tags=("block_text", block_data["id"])
        )

        # Обновляем ID элементов в блоке
        block_data["rect_id"] = rect
        block_data["text_id"] = text

        # Делаем блок интерактивным
        self.make_block_interactive(block_data)

    def level_down(self):
        """Проваливаемся в выбранный блок (переход на уровень детализации блока)"""
        if not self.selected_block:
            print("Выберите блок для перехода на уровень ниже")
            return
        
        # Проверяем, что блок принадлежит текущему уровню
        current_blocks = self.layer_manager.get_blocks_for_current_level([b["model"] for b in self.blocks])
        if self.selected_block["model"] not in current_blocks:
            print("Можно проваливаться только в блоки текущего уровня")
            return
        
        # Сохраняем состояние текущего уровня
        current_level_key = self.layer_manager.get_current_level_key()
        self.save_current_level_state(current_level_key)
        
        # Переходим на уровень детализации блока
        self.layer_manager.enter_block_level(self.selected_block["model"])
        
        # Восстанавливаем состояние нового уровня или показываем пустой
        new_level_key = self.layer_manager.get_current_level_key()
        self.restore_level_state(new_level_key)
        
        # Обновляем панель слоев, если она открыта
        if self.layers_panel_visible:
            self.update_layers_tree()
        
        self.update_footer_info()
        print(f"Перешли на уровень детализации блока {self.selected_block['model'].code}")

    def level_up(self):
        """Возврат на уровень выше"""
        if self.layer_manager.exit_level():
            # Восстанавливаем состояние предыдущего уровня
            level_key = self.layer_manager.get_current_level_key()
            self.restore_level_state(level_key)
            
            # Обновляем панель слоев, если она открыта
            if self.layers_panel_visible:
                self.update_layers_tree()
            
            self.update_footer_info()
            print(f"Вернулись на уровень выше")
        else:
            print("Уже на корневом уровне")

    def update_footer_info(self):
        """Обновляет информацию в футере о текущем уровне"""
        if hasattr(self, 'footer_right_label'):
            level_path = self.layer_manager.get_level_path([b["model"] for b in self.blocks])
            self.footer_right_label.config(text=level_path)
        
        # Проверяем ошибки нумерации
        self.check_numbering_errors()
    
    def check_numbering_errors(self):
        """Проверяет пропуски в нумерации блоков и показывает/скрывает индикатор ошибки"""
        missing_codes = self._find_missing_codes()
        
        if missing_codes:
            # Показываем индикатор ошибки
            if hasattr(self, 'error_indicator_canvas'):
                self.error_indicator_canvas.place(relx=1, rely=1, x=-40, y=-30, anchor='se')
                # Сохраняем список отсутствующих кодов для tooltip
                self.missing_codes = missing_codes
        else:
            # Скрываем индикатор ошибки
            if hasattr(self, 'error_indicator_canvas'):
                self.error_indicator_canvas.place_forget()
                if hasattr(self, 'missing_codes'):
                    self.missing_codes = []
    
    def _find_missing_codes(self):
        """Находит пропуски в нумерации блоков"""
        missing_codes = []
        
        # Проверяем корневой уровень
        root_blocks = [b for b in self.blocks if b["model"].parent_id is None]
        if root_blocks:
            used_numbers = set()
            for block_data in root_blocks:
                code = block_data["model"].code
                if code.startswith("A") and "." not in code:
                    try:
                        num = int(code[1:])
                        used_numbers.add(num)
                    except ValueError:
                        pass
            
            if used_numbers:
                max_num = max(used_numbers)
                for i in range(1, max_num + 1):
                    if i not in used_numbers:
                        missing_codes.append(f"A{i}")
        
        # Проверяем дочерние уровни
        def check_children(parent_id, parent_code):
            children = [b for b in self.blocks if b["model"].parent_id == parent_id]
            if children:
                used_numbers = set()
                for block_data in children:
                    code = block_data["model"].code
                    if code.startswith(parent_code + "."):
                        try:
                            num = int(code.split(".")[-1])
                            used_numbers.add(num)
                        except ValueError:
                            pass
                
                if used_numbers:
                    max_num = max(used_numbers)
                    for i in range(1, max_num + 1):
                        if i not in used_numbers:
                            missing_codes.append(f"{parent_code}.{i}")
                
                # Рекурсивно проверяем детей
                for block_data in children:
                    check_children(block_data["model"].id, block_data["model"].code)
        
        # Проверяем все уровни иерархии
        for root_block in root_blocks:
            check_children(root_block["model"].id, root_block["model"].code)
        
        return missing_codes
    
    def _format_missing_codes(self, codes):
        """Форматирует список недостающих кодов, группируя их в диапазоны при большом количестве"""
        if not codes:
            return ""
        
        if len(codes) <= 4:
            # Если кодов 4 или меньше, просто перечисляем их
            if len(codes) == 1:
                return codes[0]
            else:
                return ", ".join(codes)
        
        # Если кодов больше 4, группируем в диапазоны
        # Разделяем коды по префиксам (A1, A1.1, A1.2 и т.д.)
        codes_by_prefix = {}
        for code in codes:
            # Определяем префикс (A, A1, A1.1 и т.д.)
            if "." in code:
                parts = code.split(".")
                prefix = ".".join(parts[:-1])  # Все части кроме последней
                num = parts[-1]
            else:
                prefix = code[0]  # "A"
                num = code[1:]
            
            if prefix not in codes_by_prefix:
                codes_by_prefix[prefix] = []
            
            try:
                codes_by_prefix[prefix].append((int(num), code))
            except ValueError:
                # Если не число, просто добавляем как есть
                codes_by_prefix[prefix].append((999999, code))
        
        # Форматируем каждый префикс отдельно
        result_parts = []
        for prefix, code_list in codes_by_prefix.items():
            # Сортируем по номеру
            code_list.sort(key=lambda x: x[0])
            numbers = [x[0] for x in code_list]
            
            # Группируем последовательные числа в диапазоны
            ranges = []
            start = numbers[0]
            end = numbers[0]
            
            for i in range(1, len(numbers)):
                if numbers[i] == end + 1:
                    end = numbers[i]
                else:
                    if start == end:
                        ranges.append((start, start))
                    else:
                        ranges.append((start, end))
                    start = numbers[i]
                    end = numbers[i]
            
            # Добавляем последний диапазон
            if start == end:
                ranges.append((start, start))
            else:
                ranges.append((start, end))
            
            # Формируем строку для этого префикса
            prefix_parts = []
            for start_num, end_num in ranges:
                if start_num == end_num:
                    # Одиночный код
                    if prefix == "A":
                        prefix_parts.append(f"A{start_num}")
                    else:
                        prefix_parts.append(f"{prefix}.{start_num}")
                else:
                    # Диапазон
                    if prefix == "A":
                        prefix_parts.append(f"A{start_num}-A{end_num}")
                    else:
                        prefix_parts.append(f"{prefix}.{start_num}-{prefix}.{end_num}")
            
            result_parts.extend(prefix_parts)
        
        return ", ".join(result_parts)
    
    def _show_error_tooltip(self, event):
        """Показывает tooltip с информацией об ошибке"""
        if not hasattr(self, 'missing_codes') or not self.missing_codes:
            return
        
        # Создаем tooltip окно
        self.error_tooltip = tk.Toplevel(self.root)
        self.error_tooltip.wm_overrideredirect(True)
        self.error_tooltip.wm_attributes("-topmost", True)
        
        # Формируем текст ошибки
        if len(self.missing_codes) == 1:
            error_text = f"Не хватает элемента {self.missing_codes[0]}"
        else:
            error_text = f"Не хватает элементов: {', '.join(self.missing_codes)}"
        
        label = tk.Label(
            self.error_tooltip,
            text=error_text,
            font=("Segoe UI", 9),
            bg="#fff3cd",
            fg="#856404",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=4
        )
        label.pack()
        
        # Позиционируем tooltip рядом с курсором
        x = event.x_root + 10
        y = event.y_root - 30
        self.error_tooltip.geometry(f"+{x}+{y}")
    
    def _hide_error_tooltip(self, event):
        """Скрывает tooltip"""
        if self.error_tooltip:
            self.error_tooltip.destroy()
            self.error_tooltip = None
    
    def draw_arrow(self, arrow_data):
        """
        Рисует стрелку на canvas
        
        Args:
            arrow_data: Словарь с данными стрелки: {"arrow": Arrow, "line_id": int, "arrowhead_id": int}
        """
        arrow = arrow_data["arrow"]
        
        # Находим блоки для вычисления точек соединения
        from_block = None
        to_block = None
        
        if arrow.from_block_id:
            from_block = next((b["model"] for b in self.blocks if b["id"] == arrow.from_block_id), None)
            if from_block is None:
                print(f"Предупреждение: Блок {arrow.from_block_id} не найден для стрелки {arrow.id}")
        
        if arrow.to_block_id:
            to_block = next((b["model"] for b in self.blocks if b["id"] == arrow.to_block_id), None)
            if to_block is None:
                print(f"Предупреждение: Блок {arrow.to_block_id} не найден для стрелки {arrow.id}")
        
        # Вычисляем точки соединения
        print(f"Вычисление координат для стрелки {arrow.id}")
        print(f"  from_block_id={arrow.from_block_id}, to_block_id={arrow.to_block_id}")
        print(f"  from_side={arrow.from_side}, to_side={arrow.to_side}")
        print(f"  from_block найден: {from_block is not None}, to_block найден: {to_block is not None}")
        
        if from_block:
            print(f"  from_block: x={from_block.x}, y={from_block.y}, width={from_block.width}, height={from_block.height}")
        if to_block:
            print(f"  to_block: x={to_block.x}, y={to_block.y}, width={to_block.width}, height={to_block.height}")
        
        arrow.calculate_connection_points(from_block, to_block)
        
        x1, y1 = arrow.display_x1, arrow.display_y1
        x2, y2 = arrow.display_x2, arrow.display_y2
        
        print(f"  Вычисленные координаты: ({x1}, {y1}) -> ({x2}, {y2})")
        
        if x1 is None or y1 is None or x2 is None or y2 is None:
            print(f"Ошибка: Не удалось вычислить координаты для стрелки {arrow.id}")
            print(f"  from_block_id={arrow.from_block_id}, to_block_id={arrow.to_block_id}")
            print(f"  from_block={from_block}, to_block={to_block}")
            print(f"  from_side={arrow.from_side}, to_side={arrow.to_side}")
            print(f"  display_x1={x1}, display_y1={y1}, display_x2={x2}, display_y2={y2}")
            print(f"  Всего блоков: {len(self.blocks)}")
            for b in self.blocks:
                print(f"    Блок: {b['id']}")
            return  # Нельзя нарисовать стрелку без координат
        
        # Определяем стиль линии
        dash = None
        if arrow.style == "dashed":
            dash = (8, 4)
        elif arrow.style == "dotted":
            dash = (2, 2)
        
        # Удаляем старую линию и хитбокс, если существуют
        if arrow_data.get("line_id"):
            try:
                self.canvas.delete(arrow_data["line_id"])
            except tk.TclError:
                pass  # Элемент уже удален
        if arrow_data.get("hitbox_id"):
            try:
                self.canvas.delete(arrow_data["hitbox_id"])
            except tk.TclError:
                pass  # Элемент уже удален
        
        # Рисуем линию стрелки (увеличиваем толщину если стрелка выбрана)
        line_width = arrow.width + 2 if (self.selected_arrow and arrow_data == self.selected_arrow) else arrow.width
        # Используем цвет стрелки (если он не установлен, используем цвет из темы)
        arrow_color = arrow.color if arrow.color and arrow.color != Colors.ARROW_COLOR else Colors.ARROW_COLOR
        
        # Рисуем стрелку с сглаживанием для устранения "лесенки"
        # Всегда рисуем прямую стрелку - добавляем промежуточные точки для сглаживания
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
            
        # Если стрелка достаточно длинная, добавляем промежуточные точки
        if length > 10:
            # Добавляем несколько промежуточных точек для плавности
            num_points = max(3, int(length / 20))  # Одна точка на каждые 20 пикселей
            points = []
            for i in range(num_points + 1):
                t = i / num_points
                px = x1 + dx * t
                py = y1 + dy * t
                points.extend([px, py])
            
            line_id = self.canvas.create_line(
                *points,
                fill=arrow_color,
                width=line_width,
                dash=dash,
                capstyle="round",  # Круглые концы для плавности
                joinstyle="round",  # Круглые соединения
                smooth=True,  # Включаем сглаживание для плавной линии
                tags=("arrow_line", arrow.id)
            )
        else:
            # Для коротких стрелок используем простую линию
            line_id = self.canvas.create_line(
                x1, y1, x2, y2,
                fill=arrow_color,
                width=line_width,
                dash=dash,
                capstyle="round",  # Круглые концы для плавности
                joinstyle="round",  # Круглые соединения
                tags=("arrow_line", arrow.id)
            )
        arrow_data["line_id"] = line_id
        
        # Создаем невидимую широкую линию для увеличения хитбокса (для удобного захвата)
        hitbox_width = 20  # Ширина области клика
        # Используем пустой fill для полной прозрачности
        if length > 10:
            # Используем те же промежуточные точки для хитбокса
            num_points = max(3, int(length / 20))
            points = []
            for i in range(num_points + 1):
                t = i / num_points
                px = x1 + dx * t
                py = y1 + dy * t
                points.extend([px, py])
            
            hitbox_id = self.canvas.create_line(
                *points,
                fill="",  # Прозрачный цвет
                width=hitbox_width,
                dash=dash,
                capstyle="round",
                joinstyle="round",
                smooth=True,
                tags=("arrow_line", "arrow_hitbox", arrow.id),
                state="normal"  # Убеждаемся, что линия активна для клика
            )
        else:
            hitbox_id = self.canvas.create_line(
                x1, y1, x2, y2,
                fill="",  # Прозрачный цвет
                width=hitbox_width,
                dash=dash,
                capstyle="round",
                joinstyle="round",
                tags=("arrow_line", "arrow_hitbox", arrow.id),
                state="normal"  # Убеждаемся, что линия активна для клика
            )
        arrow_data["hitbox_id"] = hitbox_id
        
        # Удаляем старый наконечник, если существует
        if arrow_data.get("arrowhead_id"):
            try:
                self.canvas.delete(arrow_data["arrowhead_id"])
            except tk.TclError:
                pass  # Элемент уже удален
        
        # Рисуем наконечник стрелки
        arrowhead_id = self.create_arrowhead(x1, y1, x2, y2, arrow_color, arrow.width)
        arrow_data["arrowhead_id"] = arrowhead_id
        
        # Сохраняем ID для обновления
        if arrowhead_id:
            self.canvas.addtag_withtag(arrow.id, arrowhead_id)
        
        # Поднимаем стрелку наверх, чтобы она была поверх блоков
        # Хитбокс должен быть под видимой линией, но выше блоков
        if hitbox_id:
            self.canvas.tag_raise(hitbox_id)
        self.canvas.tag_raise(line_id)
        if arrowhead_id:
            self.canvas.tag_raise(arrowhead_id)
        
        # Удаляем старый текст и обводку, если существуют
        if arrow_data.get("text_id"):
            try:
                self.canvas.delete(arrow_data["text_id"])
            except tk.TclError:
                pass  # Элемент уже удален
        if arrow_data.get("text_outline_ids"):
            for outline_id in arrow_data["text_outline_ids"]:
                try:
                    self.canvas.delete(outline_id)
                except tk.TclError:
                    pass  # Элемент уже удален
            arrow_data["text_outline_ids"] = []
        
        # Рисуем текст на стрелке, если он есть
        if arrow.text and arrow.text.strip():
            # Вычисляем вектор направления стрелки
            # Для прямой стрелки
            dx = x2 - x1
            dy = y2 - y1
            # Позиция текста - середина линии
            base_x = (x1 + x2) / 2
            base_y = (y1 + y2) / 2
            
            # Вычисляем длину вектора направления
            length = math.sqrt(dx * dx + dy * dy)
            if length == 0:
                length = 1  # Избегаем деления на ноль
            
            # Нормализуем вектор направления
            dx_norm = dx / length
            dy_norm = dy / length
            
            # Вычисляем нормальный вектор (перпендикулярный к стрелке)
            # Поворачиваем вектор направления на 90 градусов против часовой стрелки
            normal_x = -dy_norm
            normal_y = dx_norm
            
            # Смещаем текст перпендикулярно к стрелке
            # Расстояние смещения (в пикселях)
            offset_distance = 20  # Смещение от стрелки
            
            # Вычисляем финальную позицию текста
            text_x = base_x + normal_x * offset_distance
            text_y = base_y + normal_y * offset_distance
            
            # Вычисляем угол наклона стрелки для поворота текста (параллельно стрелке)
            angle_rad = math.atan2(dy, dx)
            angle = angle_rad * 180 / math.pi
            
            # Исправляем угол, чтобы текст не был перевернутым
            # Если угол больше 90 или меньше -90, поворачиваем на 180 градусов
            if angle > 90 or angle < -90:
                angle = angle + 180 if angle < 0 else angle - 180
            
            # Цвет текста зависит от темы, а не от цвета стрелки
            text_color = Colors.TEXT_PRIMARY
            # Обводка текста - противоположный цвет от цвета текста темы
            def get_opposite_color(color):
                """Возвращает противоположный цвет (инвертированный RGB)"""
                try:
                    # Убираем # если есть
                    color = color.lstrip('#')
                    # Конвертируем в RGB
                    r = int(color[0:2], 16)
                    g = int(color[2:4], 16)
                    b = int(color[4:6], 16)
                    # Инвертируем
                    r = 255 - r
                    g = 255 - g
                    b = 255 - b
                    # Возвращаем в формате #RRGGBB
                    return f"#{r:02x}{g:02x}{b:02x}"
                except:
                    # Если не удалось обработать, возвращаем белый или черный
                    return "#FFFFFF" if text_color != "#FFFFFF" else "#000000"
            
            outline_color = get_opposite_color(text_color)
            
            # Создаем обводку текста (рисуем текст несколько раз со смещением)
            outline_width = 2  # Толщина обводки
            outline_ids = []
            for dx_offset in range(-outline_width, outline_width + 1):
                for dy_offset in range(-outline_width, outline_width + 1):
                    if dx_offset == 0 and dy_offset == 0:
                        continue  # Пропускаем центральную позицию
                    outline_id = self.canvas.create_text(
                        text_x + dx_offset, text_y + dy_offset,
                        text=arrow.text,
                        font=("Segoe UI", 9, "bold"),
                        fill=outline_color,
                        angle=angle,
                        tags=("arrow_text_outline", arrow.id)
                    )
                    outline_ids.append(outline_id)
            
            # Создаем основной текст на стрелке поверх обводки
            text_id = self.canvas.create_text(
                text_x, text_y,
                text=arrow.text,
                font=("Segoe UI", 9, "bold"),
                fill=text_color,
                angle=angle,
                tags=("arrow_text", arrow.id)
            )
            arrow_data["text_id"] = text_id
            arrow_data["text_outline_ids"] = outline_ids
            
            # Поднимаем текст наверх (сначала обводка, потом основной текст)
            for outline_id in outline_ids:
                self.canvas.tag_raise(outline_id)
            self.canvas.tag_raise(text_id)
        
        # Обновляем маркеры и кнопки, если стрелка выбрана
        if self.selected_arrow == arrow_data:
            self.update_arrow_drag_handles(arrow_data)
            self.update_arrow_action_buttons_position(arrow_data)
        
        print(f"Нарисована стрелка {arrow.id}: ({x1:.1f}, {y1:.1f}) -> ({x2:.1f}, {y2:.1f})")
    
    def create_arrowhead(self, x1, y1, x2, y2, color, width):
        """
        Создает наконечник стрелки в виде треугольника
        
        Args:
            x1, y1: Координаты начала стрелки
            x2, y2: Координаты конца стрелки
            color: Цвет наконечника
            width: Толщина линии (влияет на размер наконечника)
            
        Returns:
            ID созданного полигона наконечника
        """
        # Размер наконечника зависит от толщины линии
        arrowhead_size = max(8, width * 3)
        
        # Вычисляем угол наклона стрелки
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Координаты треугольника наконечника
        # Вершина наконечника находится на конце стрелки
        # Отступаем немного назад от конца стрелки
        back_distance = arrowhead_size * 0.8
        tip_x = x2 - math.cos(angle) * back_distance
        tip_y = y2 - math.sin(angle) * back_distance
        
        # Боковые точки треугольника
        side_angle = angle + math.pi / 2
        side_length = arrowhead_size / 2
        
        point1_x = tip_x + math.cos(side_angle) * side_length
        point1_y = tip_y + math.sin(side_angle) * side_length
        
        point2_x = tip_x - math.cos(side_angle) * side_length
        point2_y = tip_y - math.sin(side_angle) * side_length
        
        # Создаем треугольник (наконечник)
        arrowhead_id = self.canvas.create_polygon(
            x2, y2,  # Вершина наконечника
            point1_x, point1_y,  # Левая точка
            point2_x, point2_y,  # Правая точка
            fill=color,
            outline=color,
            tags=("arrow_arrowhead",)
        )
        
        return arrowhead_id
    
    def draw_all_arrows(self):
        """Отрисовывает все стрелки на canvas"""
        for arrow_data in self.arrows:
            self.draw_arrow(arrow_data)
    
    def update_arrows_for_block(self, block_id):
        """
        Обновляет позиции всех стрелок, соединенных с указанным блоком
        
        Args:
            block_id: ID блока, который был перемещен
        """
        for arrow_data in self.arrows:
            arrow = arrow_data["arrow"]
            if arrow.is_connected_to_block(block_id):
                self.draw_arrow(arrow_data)
    
    def create_arrow_between_blocks(self, from_block_id, to_block_id, 
                                    from_side="right", to_side="left"):
        """
        Создает стрелку между двумя блоками
        
        Args:
            from_block_id: ID начального блока
            to_block_id: ID конечного блока
            from_side: Сторона начального блока
            to_side: Сторона конечного блока
            
        Returns:
            Словарь с данными стрелки
        """
        # Проверяем, что блоки существуют
        from_block_data = next((b for b in self.blocks if b["id"] == from_block_id), None)
        to_block_data = next((b for b in self.blocks if b["id"] == to_block_id), None)
        
        if from_block_data is None:
            print(f"Ошибка: Блок {from_block_id} не найден!")
            return None
        if to_block_data is None:
            print(f"Ошибка: Блок {to_block_id} не найден!")
            return None
        
        arrow_id = f"arrow_{self.next_arrow_id}"
        self.next_arrow_id += 1
        
        arrow = Arrow(
            arrow_id=arrow_id,
            from_block_id=from_block_id,
            to_block_id=to_block_id,
            from_side=from_side,
            to_side=to_side,
            color=Colors.ARROW_COLOR  # Используем цвет из темы
        )
        
        arrow_data = {
            "arrow": arrow,
            "line_id": None,
            "arrowhead_id": None
        }
        
        self.arrows.append(arrow_data)
        print(f"Добавлена стрелка в список, всего стрелок: {len(self.arrows)}")
        
        # Рисуем стрелку
        self.draw_arrow(arrow_data)
        
        print(f"Создана стрелка {arrow_id} от {from_block_id} к {to_block_id}")
        return arrow_data
    
    def create_arrow_from_block_to_point(self, from_block_id, x, y):
        """Создает стрелку от блока к точке на холсте"""
        from_block_data = next((b for b in self.blocks if b["id"] == from_block_id), None)
        if from_block_data is None:
            print(f"Ошибка: Блок {from_block_id} не найден!")
            return None
        
        arrow_id = f"arrow_{self.next_arrow_id}"
        self.next_arrow_id += 1
        
        # Определяем сторону блока на основе направления к точке
        from_block = from_block_data["model"]
        dx = x - from_block.x
        dy = y - from_block.y
        
        if abs(dx) > abs(dy):
            from_side = "right" if dx > 0 else "left"
        else:
            from_side = "bottom" if dy > 0 else "top"
        
        arrow = Arrow(
            arrow_id=arrow_id,
            from_block_id=from_block_id,
            to_block_id=None,
            from_side=from_side,
            to_side=None,
            x2=x,
            y2=y,
            color=Colors.ARROW_COLOR  # Используем цвет из темы
        )
        
        arrow_data = {
            "arrow": arrow,
            "line_id": None,
            "arrowhead_id": None
        }
        
        self.arrows.append(arrow_data)
        self.draw_arrow(arrow_data)
        print(f"Создана стрелка {arrow_id} от блока {from_block_id} к точке ({x:.1f}, {y:.1f})")
        return arrow_data
    
    def create_arrow_from_point_to_block(self, x, y, to_block_id):
        """Создает стрелку от точки на холсте к блоку"""
        to_block_data = next((b for b in self.blocks if b["id"] == to_block_id), None)
        if to_block_data is None:
            print(f"Ошибка: Блок {to_block_id} не найден!")
            return None
        
        arrow_id = f"arrow_{self.next_arrow_id}"
        self.next_arrow_id += 1
        
        # Определяем сторону блока на основе направления от точки
        to_block = to_block_data["model"]
        dx = to_block.x - x
        dy = to_block.y - y
        
        if abs(dx) > abs(dy):
            to_side = "left" if dx > 0 else "right"
        else:
            to_side = "top" if dy > 0 else "bottom"
        
        arrow = Arrow(
            arrow_id=arrow_id,
            from_block_id=None,
            to_block_id=to_block_id,
            from_side=None,
            to_side=to_side,
            x1=x,
            y1=y,
            color=Colors.ARROW_COLOR  # Используем цвет из темы
        )
        
        arrow_data = {
            "arrow": arrow,
            "line_id": None,
            "arrowhead_id": None
        }
        
        self.arrows.append(arrow_data)
        self.draw_arrow(arrow_data)
        print(f"Создана стрелка {arrow_id} от точки ({x:.1f}, {y:.1f}) к блоку {to_block_id}")
        return arrow_data
    
    def create_arrow_from_point_to_point(self, x1, y1, x2, y2):
        """Создает стрелку от точки к точке на холсте"""
        arrow_id = f"arrow_{self.next_arrow_id}"
        self.next_arrow_id += 1
        
        arrow = Arrow(
            arrow_id=arrow_id,
            from_block_id=None,
            to_block_id=None,
            from_side=None,
            to_side=None,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            color=Colors.ARROW_COLOR  # Используем цвет из темы
        )
        
        arrow_data = {
            "arrow": arrow,
            "line_id": None,
            "arrowhead_id": None
        }
        
        self.arrows.append(arrow_data)
        self.draw_arrow(arrow_data)
        print(f"Создана стрелка {arrow_id} от точки ({x1:.1f}, {y1:.1f}) к точке ({x2:.1f}, {y2:.1f})")
        return arrow_data
    
    def delete_selected(self):
        """Удаляет выбранный элемент (блок или стрелку)"""
        if self.selected_block:
            # Используем delete_block для правильной перенумерации
            self.delete_block(self.selected_block)
            
            print(f"Блок удален")
        elif self.selected_arrow:
            # Удаляем стрелку
            self.delete_arrow(self.selected_arrow)
            self.selected_arrow = None
            self.properties_panel.update_properties(None)
            
            # Сохраняем состояние для undo
            self.save_state()
            
            print(f"Стрелка удалена")
    
    def delete_arrow(self, arrow_data):
        """Удаляет стрелку"""
        # Скрываем инструменты перед удалением (всегда, не только если выбрана)
        if self.selected_arrow == arrow_data:
            self.selected_arrow = None
        # Удаляем инструменты в любом случае, чтобы они не оставались на холсте
        self.hide_arrow_action_buttons()
        self.delete_arrow_drag_handles()
        self.hide_attachment_points()
        
        if arrow_data.get("line_id"):
            self.canvas.delete(arrow_data["line_id"])
        if arrow_data.get("hitbox_id"):
            self.canvas.delete(arrow_data["hitbox_id"])
        if arrow_data.get("arrowhead_id"):
            self.canvas.delete(arrow_data["arrowhead_id"])
        if arrow_data.get("text_id"):
            self.canvas.delete(arrow_data["text_id"])
        if arrow_data.get("text_outline_ids"):
            for outline_id in arrow_data["text_outline_ids"]:
                try:
                    self.canvas.delete(outline_id)
                except tk.TclError:
                    pass
        if arrow_data in self.arrows:
            self.arrows.remove(arrow_data)
    
    def save_state(self):
        """Сохраняет текущее состояние для undo/redo"""
        state = {
            "blocks": [],
            "arrows": [],
            "next_block_id": self.next_block_id,
            "next_arrow_id": self.next_arrow_id
        }
        
        # Сохраняем все блоки
        for block_data in self.blocks:
            block = block_data["model"]
            state["blocks"].append({
                "id": block.id,
                "name": block.name,
                "code": block.code,
                "element_type": block.element_type,
                "description": block.description,
                "x": block.x,
                "y": block.y,
                "width": block.width,
                "height": block.height,
                "color": block.color,
                "border_width": block.border_width
            })
        
        # Сохраняем все стрелки
        for arrow_data in self.arrows:
            arrow = arrow_data["arrow"]
            state["arrows"].append({
                "id": arrow.id,
                "from_block_id": arrow.from_block_id,
                "to_block_id": arrow.to_block_id,
                "from_side": arrow.from_side,
                "to_side": arrow.to_side,
                "from_attachment_point": arrow.from_attachment_point,
                "to_attachment_point": arrow.to_attachment_point,
                "color": arrow.color,
                "width": arrow.width,
                "style": arrow.style,
                "x1": arrow.x1,
                "y1": arrow.y1,
                "x2": arrow.x2,
                "y2": arrow.y2,
                "bend_x": arrow.bend_x,
                "bend_y": arrow.bend_y,
                "text": arrow.text if hasattr(arrow, 'text') else ""
            })
        
        # Добавляем в стек undo
        self.undo_stack.append(state)
        
        # Ограничиваем размер стека
        if len(self.undo_stack) > self.max_history_size:
            self.undo_stack.pop(0)
        
        # Очищаем redo при новом действии
        self.redo_stack = []
        
        # Обновляем состояние кнопок
        self.update_undo_redo_buttons()
    
    def restore_state(self, state):
        """Восстанавливает состояние из сохраненного снимка"""
        # Очищаем canvas полностью
        self.canvas.delete("all")
        self.draw_grid()
        
        # Восстанавливаем счетчики
        self.next_block_id = state["next_block_id"]
        self.next_arrow_id = state["next_arrow_id"]
        
        # Очищаем списки
        self.blocks = []
        self.arrows = []
        self.selected_block = None
        self.selected_arrow = None
        
        # Восстанавливаем блоки (только данные, без визуализации)
        for block_dict in state["blocks"]:
            block = Block(
                block_id=block_dict["id"],
                name=block_dict["name"],
                code=block_dict["code"],
                element_type=block_dict["element_type"],
                description=block_dict["description"],
                x=block_dict["x"],
                y=block_dict["y"],
                width=block_dict["width"],
                height=block_dict["height"],
                color=block_dict["color"],
                border_width=block_dict["border_width"],
                parent_id=block_dict.get("parent_id")
            )
            
            # Создаем block_data без визуальных элементов (они будут созданы в refresh_canvas)
            block_data = {
                "id": block.id,
                "model": block,
                "rect_id": None,  # Будет создан в refresh_canvas
                "text_id": None,  # Будет создан в refresh_canvas
                "resize_handles": {}
            }
            
            self.blocks.append(block_data)
        
        # Восстанавливаем стрелки
        for arrow_dict in state["arrows"]:
            arrow = Arrow(
                arrow_id=arrow_dict["id"],
                from_block_id=arrow_dict["from_block_id"],
                to_block_id=arrow_dict["to_block_id"],
                from_side=arrow_dict["from_side"],
                to_side=arrow_dict["to_side"],
                color=arrow_dict["color"],
                width=arrow_dict["width"],
                style=arrow_dict["style"],
                x1=arrow_dict["x1"],
                y1=arrow_dict["y1"],
                x2=arrow_dict["x2"],
                y2=arrow_dict["y2"],
                text=arrow_dict.get("text", "")
            )
            arrow.from_attachment_point = arrow_dict.get("from_attachment_point")
            arrow.to_attachment_point = arrow_dict.get("to_attachment_point")
            arrow.bend_x = arrow_dict.get("bend_x")
            arrow.bend_y = arrow_dict.get("bend_y")
            
            arrow_data = {
                "arrow": arrow
            }
            
            self.arrows.append(arrow_data)
            self.draw_arrow(arrow_data)
        
        # Обновляем панель свойств
        self.properties_panel.update_properties(None)
    
    def undo(self):
        """Отменяет последнее действие"""
        if not self.undo_stack:
            return
        
        # Сохраняем текущее состояние в redo
        current_state = self.save_current_state()
        if current_state:
            self.redo_stack.append(current_state)
            if len(self.redo_stack) > self.max_history_size:
                self.redo_stack.pop(0)
        
        # Восстанавливаем предыдущее состояние
        previous_state = self.undo_stack.pop()
        self.restore_state(previous_state)
        
        # Обновляем canvas для текущего уровня
        self.refresh_canvas()
        
        # Обновляем состояние кнопок
        self.update_undo_redo_buttons()
    
    def redo(self):
        """Повторяет отмененное действие"""
        if not self.redo_stack:
            return
        
        # Сохраняем текущее состояние в undo
        current_state = self.save_current_state()
        if current_state:
            self.undo_stack.append(current_state)
            if len(self.undo_stack) > self.max_history_size:
                self.undo_stack.pop(0)
        
        # Восстанавливаем состояние из redo
        next_state = self.redo_stack.pop()
        self.restore_state(next_state)
        
        # Обновляем canvas для текущего уровня
        self.refresh_canvas()
        
        # Обновляем состояние кнопок
        self.update_undo_redo_buttons()
    
    def save_current_state(self):
        """Сохраняет текущее состояние без добавления в стек (для undo/redo)"""
        state = {
            "blocks": [],
            "arrows": [],
            "next_block_id": self.next_block_id,
            "next_arrow_id": self.next_arrow_id
        }
        
        # Сохраняем все блоки
        for block_data in self.blocks:
            block = block_data["model"]
            state["blocks"].append({
                "id": block.id,
                "name": block.name,
                "code": block.code,
                "element_type": block.element_type,
                "description": block.description,
                "x": block.x,
                "y": block.y,
                "width": block.width,
                "height": block.height,
                "color": block.color,
                "border_width": block.border_width,
                "parent_id": block.parent_id
            })
        
        # Сохраняем все стрелки
        for arrow_data in self.arrows:
            arrow = arrow_data["arrow"]
            state["arrows"].append({
                "id": arrow.id,
                "from_block_id": arrow.from_block_id,
                "to_block_id": arrow.to_block_id,
                "from_side": arrow.from_side,
                "to_side": arrow.to_side,
                "from_attachment_point": arrow.from_attachment_point,
                "to_attachment_point": arrow.to_attachment_point,
                "color": arrow.color,
                "width": arrow.width,
                "style": arrow.style,
                "x1": arrow.x1,
                "y1": arrow.y1,
                "x2": arrow.x2,
                "y2": arrow.y2,
                "bend_x": arrow.bend_x,
                "bend_y": arrow.bend_y,
                "text": arrow.text if hasattr(arrow, 'text') else ""
            })
        
        return state
    
    def update_undo_redo_buttons(self):
        """Обновляет состояние кнопок undo/redo (активны/неактивны)"""
        if hasattr(self, 'undo_btn'):
            if self.undo_stack:
                self.undo_btn.configure(state="normal")
            else:
                self.undo_btn.configure(state="disabled")
        
        if hasattr(self, 'redo_btn'):
            if self.redo_stack:
                self.redo_btn.configure(state="normal")
            else:
                self.redo_btn.configure(state="disabled")
    
    def new_file(self):
        """Создает новый файл"""
        if messagebox.askyesno("Новый файл", "Создать новый файл? Все несохраненные изменения будут потеряны."):
            # Очищаем все
            self.blocks = []
            self.arrows = []
            self.selected_block = None
            self.selected_arrow = None
            self.next_block_id = 1
            self.next_arrow_id = 1
            self.layer_manager = LayerManager()
            self.undo_stack = []
            self.redo_stack = []
            
            # Очищаем canvas
            self.canvas.delete("all")
            self.draw_grid()
            
            # Обновляем панель свойств
            self.properties_panel.update_properties(None)
            self.update_footer_info()
            if self.layers_panel_visible:
                self.update_layers_tree()
    
    def save_file(self):
        """Сохраняет текущий файл"""
        if not hasattr(self, 'current_file_path') or not self.current_file_path:
            self.save_file_as()
        else:
            self._save_to_file(self.current_file_path)
    
    def save_file_as(self):
        """Сохраняет файл с выбором пути"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file_path = file_path
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path):
        """Сохраняет данные в файл"""
        try:
            state = self.save_current_state()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранение", "Файл успешно сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def open_file(self):
        """Открывает файл"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Сбрасываем уровень на корневой перед восстановлением
                self.layer_manager.current_level_path = []
                
                # Восстанавливаем состояние
                self.restore_state(state)
                self.current_file_path = file_path
                
                # Обновляем canvas для текущего уровня (показываем только корневой уровень)
                self.refresh_canvas()
                
                # Обновляем интерфейс
                self.update_footer_info()
                if self.layers_panel_visible:
                    self.update_layers_tree()
                
                messagebox.showinfo("Открытие", "Файл успешно открыт!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def copy_selected(self):
        """Копирует выбранный элемент (блок или стрелку) в буфер обмена"""
        if self.selected_block:
            # Сохраняем данные блока
            block = self.selected_block["model"]
            self.clipboard = {
                "id": block.id,
                "name": block.name,
                "code": block.code,
                "element_type": block.element_type,
                "description": block.description,
                "x": block.x,
                "y": block.y,
                "width": block.width,
                "height": block.height,
                "color": block.color,
                "border_width": block.border_width,
                "parent_id": block.parent_id
            }
            self.clipboard_type = "block"
        elif self.selected_arrow:
            # Сохраняем данные стрелки
            arrow = self.selected_arrow["arrow"]
            self.clipboard = {
                "id": arrow.id,
                "from_block_id": arrow.from_block_id,
                "to_block_id": arrow.to_block_id,
                "from_side": arrow.from_side,
                "to_side": arrow.to_side,
                "from_attachment_point": arrow.from_attachment_point,
                "to_attachment_point": arrow.to_attachment_point,
                "color": arrow.color,
                "width": arrow.width,
                "style": arrow.style,
                "x1": arrow.x1,
                "y1": arrow.y1,
                "x2": arrow.x2,
                "y2": arrow.y2,
                "bend_x": arrow.bend_x,
                "bend_y": arrow.bend_y,
                "text": arrow.text if hasattr(arrow, 'text') else "",
                "display_x1": arrow.display_x1,
                "display_y1": arrow.display_y1,
                "display_x2": arrow.display_x2,
                "display_y2": arrow.display_y2
            }
            self.clipboard_type = "arrow"
    
    def cut_selected(self):
        """Вырезает выбранный элемент (копирует и удаляет)"""
        if not self.selected_block and not self.selected_arrow:
            return
        
        # Копируем в буфер обмена
        self.copy_selected()
        
        # Удаляем элемент
        if self.selected_block:
            self.delete_block_direct(self.selected_block)
        elif self.selected_arrow:
            self.delete_arrow_direct(self.selected_arrow)
        
        # Сохраняем состояние для undo
        self.save_state()
    
    def paste_clipboard(self):
        """Вставляет элемент из буфера обмена"""
        if not self.clipboard or not self.clipboard_type:
            return
        
        if self.clipboard_type == "block":
            # Создаем новый блок со смещением
            offset = 30
            block_data = self.clipboard
            new_block = Block(
                block_id=None,  # Будет создан новый ID
                name=block_data["name"],
                code=block_data["code"],
                element_type=block_data["element_type"],
                description=block_data["description"],
                x=block_data["x"] + offset,
                y=block_data["y"] + offset,
                width=block_data["width"],
                height=block_data["height"],
                color=block_data["color"],
                border_width=block_data["border_width"],
                parent_id=block_data.get("parent_id")
            )
            
            # Создаем визуальное представление
            block_id = f"block_{self.next_block_id}"
            self.next_block_id += 1
            new_block.id = block_id
            
            x1 = new_block.x - new_block.width / 2
            y1 = new_block.y - new_block.height / 2
            x2 = new_block.x + new_block.width / 2
            y2 = new_block.y + new_block.height / 2
            
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=new_block.color,
                outline=Colors.BLOCK_BORDER,
                width=new_block.border_width,
                tags=("block", block_id)
            )
            
            formatted_text = self.format_block_text(new_block.name, new_block.width)
            text = self.canvas.create_text(
                new_block.x, new_block.y,
                text=formatted_text,
                font=("Segoe UI", 10),
                fill=Colors.TEXT_PRIMARY,
                justify="center",
                width=new_block.width - 10,
                tags=("block_text", block_id)
            )
            
            block_data_obj = {
                "id": block_id,
                "model": new_block,
                "rect_id": rect,
                "text_id": text,
                "resize_handles": {}
            }
            
            self.blocks.append(block_data_obj)
            self.make_block_interactive(block_data_obj)
            self.select_block(block_data_obj)
            
        elif self.clipboard_type == "arrow":
            # Создаем новую стрелку со смещением
            offset = 30
            arrow_data = self.clipboard
            
            new_arrow_data = None
            # Если есть координаты отображения, используем их
            if arrow_data.get("display_x1") and arrow_data.get("display_y1") and \
               arrow_data.get("display_x2") and arrow_data.get("display_y2"):
                new_arrow_data = self.create_arrow_from_point_to_point(
                    arrow_data["display_x1"] + offset,
                    arrow_data["display_y1"] + offset,
                    arrow_data["display_x2"] + offset,
                    arrow_data["display_y2"] + offset
                )
            elif arrow_data.get("x1") and arrow_data.get("y1") and \
                 arrow_data.get("x2") and arrow_data.get("y2"):
                new_arrow_data = self.create_arrow_from_point_to_point(
                    arrow_data["x1"] + offset,
                    arrow_data["y1"] + offset,
                    arrow_data["x2"] + offset,
                    arrow_data["y2"] + offset
                )
            
            # Восстанавливаем свойства стрелки
            if new_arrow_data:
                new_arrow = new_arrow_data["arrow"]
                new_arrow.text = arrow_data.get("text", "")
                new_arrow.color = arrow_data.get("color", Colors.ARROW_COLOR)
                new_arrow.width = arrow_data.get("width", 2)
                new_arrow.style = arrow_data.get("style", "solid")
                new_arrow.bend_x = arrow_data.get("bend_x")
                new_arrow.bend_y = arrow_data.get("bend_y")
                self.draw_arrow(new_arrow_data)
                self.select_arrow(new_arrow_data)
        
        # Сохраняем состояние для undo
        self.save_state()
    
    def show_documentation(self):
        """Показывает окно с документацией и горячими клавишами"""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Документация - Горячие клавиши")
        doc_window.geometry("600x700")
        doc_window.configure(bg=Colors.BACKGROUND)
        
        # Создаем прокручиваемую область
        canvas = tk.Canvas(doc_window, bg=Colors.BACKGROUND, highlightthickness=0)
        scrollbar = tk.Scrollbar(doc_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BACKGROUND)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        title_label = tk.Label(
            scrollable_frame,
            text="Горячие клавиши IDEF0 Editor",
            font=("Segoe UI", 16, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT_PRIMARY
        )
        title_label.pack(pady=20)
        
        # Раздел: Редактирование
        section1 = tk.Label(
            scrollable_frame,
            text="Редактирование",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        section1.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        shortcuts_edit = [
            ("Ctrl + C", "Копировать выбранный элемент"),
            ("Ctrl + V", "Вставить элемент из буфера обмена"),
            ("Ctrl + X", "Вырезать выбранный элемент"),
            ("Ctrl + Z", "Отменить последнее действие"),
            ("Ctrl + Y", "Повторить отмененное действие"),
            ("Delete", "Удалить выбранный элемент"),
        ]
        
        for key, desc in shortcuts_edit:
            frame = tk.Frame(scrollable_frame, bg=Colors.BACKGROUND)
            frame.pack(fill=tk.X, padx=20, pady=2)
            tk.Label(
                frame,
                text=key,
                font=("Segoe UI", 10, "bold"),
                bg=Colors.BACKGROUND,
                fg=Colors.PRIMARY,
                width=15,
                anchor="w"
            ).pack(side=tk.LEFT)
            tk.Label(
                frame,
                text=desc,
                font=("Segoe UI", 10),
                bg=Colors.BACKGROUND,
                fg=Colors.TEXT_PRIMARY,
                anchor="w"
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Раздел: Навигация
        section2 = tk.Label(
            scrollable_frame,
            text="Навигация",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        section2.pack(fill=tk.X, padx=20, pady=(20, 5))
        
        shortcuts_nav = [
            ("Space", "Панорамирование холста (удерживать)"),
            ("Ctrl + Колесо мыши", "Масштабирование"),
        ]
        
        for key, desc in shortcuts_nav:
            frame = tk.Frame(scrollable_frame, bg=Colors.BACKGROUND)
            frame.pack(fill=tk.X, padx=20, pady=2)
            tk.Label(
                frame,
                text=key,
                font=("Segoe UI", 10, "bold"),
                bg=Colors.BACKGROUND,
                fg=Colors.PRIMARY,
                width=15,
                anchor="w"
            ).pack(side=tk.LEFT)
            tk.Label(
                frame,
                text=desc,
                font=("Segoe UI", 10),
                bg=Colors.BACKGROUND,
                fg=Colors.TEXT_PRIMARY,
                anchor="w"
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязываем прокрутку колесом мыши
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def run(self):
        """Запуск приложения"""
        # Устанавливаем фокус на canvas при запуске
        if hasattr(self, 'canvas'):
            self.root.after(100, lambda: self.canvas.focus_set())
        self.root.mainloop()
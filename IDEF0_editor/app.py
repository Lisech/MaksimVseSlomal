"""
Чистый макет приложения - точная копия HTML макета
Все кнопки с заглушками
"""

import tkinter as tk
from tkinter import ttk
import os
import math
from styles import Colors, Dimensions, Fonts
from properties import PropertiesPanel
from PIL import Image, ImageTk
from models import Block, Arrow

class IDEF0App:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        self.blocks = []
        self.arrows = []  # список стрелок
        self.next_block_id = 1
        self.next_arrow_id = 1  # счетчик для ID стрелок
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
        self.resize_handle_size = 8  # размер маркеров изменения размера
        self.resize_preview = None  # превью растягивания
        self.arrow_drawing_mode = False  # режим рисования стрелок
        self.arrow_start_block = None  # начальный блок для стрелки (если стрелка начинается от блока)
        self.arrow_start_x = None  # начальная координата X (если стрелка начинается не от блока)
        self.arrow_start_y = None  # начальная координата Y (если стрелка начинается не от блока)
        self.arrow_preview_line = None  # превью линии стрелки
        self.arrow_drawing = False  # флаг активного рисования стрелки
    
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

        # Подготовка кэш-словаря для иконок
        self._icons = getattr(self, '_icons', {})

        toolbar_buttons = [
            ("Новый", "FileText", (20,20)),
            ("Открыть", "FolderOpen", (20,20)),
            ("Сохранить", "Save", (20,20)),
            ("Сохранить как", "Download", (20,20))
        ]

        for text, icon_name, size in toolbar_buttons:
            icon = self.load_icon(icon_name, size)
            btn = self.create_toolbar_button(toolbar_frame, text, icon)
            btn.pack(side=tk.LEFT, padx=6)

        # Spacer
        spacer = tk.Frame(header_frame, bg=Colors.SURFACE)
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Right controls
        right_frame = tk.Frame(header_frame, bg=Colors.SURFACE)
        right_frame.pack(side=tk.RIGHT, padx=14)

        # Zoom controls
        zoom_frame = tk.Frame(right_frame, bg=Colors.SURFACE)
        zoom_frame.pack(side=tk.LEFT, padx=(0, 12))
        
        # Zoom out button
        zoom_out_icon = self.load_icon("ZoomOut", (16,16))
        zoom_out_btn = tk.Button(
            zoom_frame,
            image=zoom_out_icon,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground="#e2e8f0",
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        zoom_out_btn.image = zoom_out_icon
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(zoom_out_btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")
        
        # Zoom percentage
        tk.Label(zoom_frame, text="100%", bg=Colors.SURFACE, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=4)
        
        # Zoom in button
        zoom_in_icon = self.load_icon("ZoomIn", (16,16))
        zoom_in_btn = tk.Button(
            zoom_frame,
            image=zoom_in_icon,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            activebackground="#e2e8f0",
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        zoom_in_btn.image = zoom_in_icon
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        self.apply_hover_effect(zoom_in_btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")

        # Other buttons
        right_buttons = [("Обучение", "BookOpen"), ("Документация", "HelpCircle")]
        for text, icon_name in right_buttons:
            icon = self.load_icon(icon_name, (20,20))
            btn = self.create_toolbar_button(right_frame, text, icon)
            btn.pack(side=tk.LEFT, padx=6)

        settings_btn = self.create_toolbar_button(right_frame, "", self.load_icon("Settings", (20,20)))
        settings_btn.pack(side=tk.LEFT, padx=6)

    def create_toolbar_button(self, parent, text, icon=None):
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
            activebackground="#e2e8f0",
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        if icon is not None:
            btn.configure(image=icon, compound='left')
            btn.image = icon  # сохранить ссылку, чтобы не удалился
        self.apply_hover_effect(btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")
        return btn

    def setup_main_layout(self):
        """Основная layout-сетка как в HTML"""
        main_frame = tk.Frame(self.root, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

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

        tools = [
            ("MousePointer2", "Выбрать"),
            ("Hand", "Перемещать"),
            ("Square", "Добавить блок"),
            ("ArrowRight", "Добавить стрелку"),
            ("Move", "Переместить"),
            ("Type", "Текст"),
            ("Layers", "Слои"),
            ("ChevronUp", "На передний план"),
            ("ChevronDown", "На задний план"),
            ("Trash2", "Удалить")
        ]

        for i, (icon_name, tooltip) in enumerate(tools):
            icon = self.load_icon(icon_name, (26, 26))
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
                activebackground="#e2e8f0"
            )
            btn.configure(image=icon, compound='center', padx=16, pady=16)
            btn.image = icon

            if icon_name == "MousePointer2":
                btn.configure(command=self.enable_select_mode)

            if icon_name == "Hand":
                btn.configure(command=self.enable_pan_mode)
            
            if icon_name == "ArrowRight":
                btn.configure(command=self.enable_arrow_mode)
            
            if icon_name == "Trash2":
                btn.configure(command=self.delete_selected)

            # Привязываем обработчики для кнопки добавления блока ТОЛЬКО drag-and-drop
            if icon_name == "Square":
                # Убираем команду клика, оставляем только drag-and-drop
                btn.configure(command=None)
                # Добавляем обработчики для drag-and-drop
                btn.bind("<ButtonPress-1>", self.start_drag_from_sidebar)
                btn.bind("<B1-Motion>", self.drag_from_sidebar)
                btn.bind("<ButtonRelease-1>", self.end_drag_from_sidebar)

            self.apply_hover_effect(btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")
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
        """Создает блок в указанной позиции"""
        # Базовые размеры
        width, height = 150, 80

        # Создаем блок
        block_id = f"block_{self.next_block_id}"
        self.next_block_id += 1

        # Создаем модель блока
        block_model = Block(
            block_id=block_id,
            name=f"Блок {self.next_block_id - 1}",
            code=f"A{self.next_block_id - 1}",
            x=x,
            y=y,
            width=width,
            height=height
        )

        # Рисуем прямоугольник
        rect = self.canvas.create_rectangle(
        x - width / 2, y - height / 2,
        x + width / 2, y + height / 2,
        fill=block_model.color,
        outline=Colors.TEXT_PRIMARY,
        width=block_model.border_width,  # ← использовать border_width из модели
        tags=("block", block_id)
        )
        

        # Добавляем текст
        text = self.canvas.create_text(
            x, y,
            text=block_model.name,
            font=("Segoe UI", 10),
            justify="center",
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

        # Автоматически выбираем новый блок
        self.select_block(block_data)

        print(f"Добавлен новый блок через drag-and-drop: {block_id}")
        print(f"Всего блоков: {len(self.blocks)}")

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
            handle = self.canvas.create_rectangle(
                x - size/2, y - size/2,
                x + size/2, y + size/2,
                fill=Colors.PRIMARY,
                outline=Colors.SURFACE,
                width=1,
                tags=("resize_handle", block_data["id"], f"handle_{handle_type}")
            )
            block_data["resize_handles"][handle_type] = handle
            
            # Привязываем обработчики событий для маркера
            self.canvas.tag_bind(handle, "<ButtonPress-1>", 
                               lambda e, b=block_data, h=handle_type: self.start_resize(e, b, h))
            self.canvas.tag_bind(handle, "<B1-Motion>", 
                               lambda e, b=block_data, h=handle_type: self.do_resize(e, b, h))
            self.canvas.tag_bind(handle, "<ButtonRelease-1>", 
                               lambda e, b=block_data: self.end_resize(e, b))

    def delete_resize_handles(self, block_data):
        """Удаляет маркеры изменения размера"""
        for handle_id in block_data["resize_handles"].values():
            self.canvas.delete(handle_id)
        block_data["resize_handles"] = {}

    def start_resize(self, event, block_data, handle_type):
        """Начало изменения размера"""
        if self.current_mode == "select":
            self.resizing_block = block_data
            # Создаем превью для растягивания
            model = block_data["model"]
            self.resize_preview = self.canvas.create_rectangle(
                model.x - model.width/2, model.y - model.height/2,
                model.x + model.width/2, model.y + model.height/2,
                fill=model.color,
                outline=Colors.PRIMARY,
                width=2,
                dash=(4, 2),
                tags="resize_preview"
            )
            
            block_data["resize_data"] = {
                "handle_type": handle_type,
                "start_x": event.x,
                "start_y": event.y,
                "start_width": model.width,
                "start_height": model.height,
                "start_center_x": model.x,
                "start_center_y": model.y
            }
            return "break"

    def do_resize(self, event, block_data, handle_type):
        """Изменение размера блока (пока только превью)"""
        if self.resizing_block == block_data and "resize_data" in block_data and self.resize_preview:
            resize_data = block_data["resize_data"]
            
            # Вычисляем смещение
            dx = event.x - resize_data["start_x"]
            dy = event.y - resize_data["start_y"]
            
            # Вычисляем новые размеры и позицию
            new_width = resize_data["start_width"]
            new_height = resize_data["start_height"]
            new_center_x = resize_data["start_center_x"]
            new_center_y = resize_data["start_center_y"]
            
            if "e" in handle_type:  # правые маркеры
                new_width = max(50, resize_data["start_width"] + dx)
            if "w" in handle_type:  # левые маркеры
                new_width = max(50, resize_data["start_width"] - dx)
                new_center_x = resize_data["start_center_x"] + dx / 2
            if "s" in handle_type:  # нижние маркеры
                new_height = max(30, resize_data["start_height"] + dy)
            if "n" in handle_type:  # верхние маркеры
                new_height = max(30, resize_data["start_height"] - dy)
                new_center_y = resize_data["start_center_y"] + dy / 2
            
            # Обновляем превью
            x1 = new_center_x - new_width / 2
            y1 = new_center_y - new_height / 2
            x2 = new_center_x + new_width / 2
            y2 = new_center_y + new_height / 2
            self.canvas.coords(self.resize_preview, x1, y1, x2, y2)
            
            return "break"

    def end_resize(self, event, block_data):
        """Завершение изменения размера - применяем изменения"""
        if self.resizing_block == block_data and "resize_data" in block_data and self.resize_preview:
            resize_data = block_data["resize_data"]
            model = block_data["model"]
            
            # Вычисляем финальные размеры
            dx = event.x - resize_data["start_x"]
            dy = event.y - resize_data["start_y"]
            
            new_width = resize_data["start_width"]
            new_height = resize_data["start_height"]
            new_center_x = resize_data["start_center_x"]
            new_center_y = resize_data["start_center_y"]
            
            if "e" in resize_data["handle_type"]:
                new_width = max(50, resize_data["start_width"] + dx)
            if "w" in resize_data["handle_type"]:
                new_width = max(50, resize_data["start_width"] - dx)
                new_center_x = resize_data["start_center_x"] + dx / 2
            if "s" in resize_data["handle_type"]:
                new_height = max(30, resize_data["start_height"] + dy)
            if "n" in resize_data["handle_type"]:
                new_height = max(30, resize_data["start_height"] - dy)
                new_center_y = resize_data["start_center_y"] + dy / 2
            
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
            
            # Обновляем стрелки, соединенные с этим блоком
            self.update_arrows_for_block(block_data["id"])
            
            # Обновляем свойства
            if self.selected_block == block_data:
                self.properties_panel.update_properties(model)
            
            del block_data["resize_data"]
            self.resizing_block = None
            
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
        
        # Обновляем текст
        self.canvas.coords(block_data["text_id"], model.x, model.y)
        
        # Обновляем маркеры изменения размера
        if block_data == self.selected_block:
            self.create_resize_handles(block_data)
        
        # Обновляем стрелки, соединенные с этим блоком
        self.update_arrows_for_block(block_data["id"])

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

                # Обновляем свойства позиции
                if self.selected_block == block_data:
                    self.properties_panel.update_properties(block_data["model"])
                
                # Останавливаем распространение события
                return "break"

        def end_drag(event):
            if self.dragging_block == block_data and "drag_data" in block_data:
                del block_data["drag_data"]
                self.dragging_block = None
                print(f"Блок {block_data['id']} перемещен в ({block_data['model'].x:.1f}, {block_data['model'].y:.1f})")

        def double_click(event):
            """Обработчик двойного клика для выбора блока"""
            if self.current_mode == "select":
                self.select_block(block_data)
                return "break"
        
        def arrow_click(event):
            """Обработчик клика по блоку в режиме рисования стрелок"""
            # В новом режиме рисования стрелок клик обрабатывается в on_canvas_click
            # Этот обработчик больше не используется, но оставляем для совместимости
            if self.current_mode == "draw_arrow":
                # Разрешаем обработку в on_canvas_click
                return None
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
        # Сбрасываем выделение предыдущего блока
        if self.selected_block:
            self.canvas.itemconfig(self.selected_block["rect_id"], outline=Colors.TEXT_PRIMARY, width=2)
            self.delete_resize_handles(self.selected_block)
        
        # Сбрасываем выделение стрелки, если была выбрана
        if self.selected_arrow:
            self.deselect_arrow()
        
        # Выделяем новый блок
        self.selected_block = block_data
        self.canvas.itemconfig(block_data["rect_id"], outline=Colors.PRIMARY, width=3)
        
        # Создаем маркеры изменения размера
        self.create_resize_handles(block_data)
        
        # Обновляем панель свойств
        self.properties_panel.update_properties(block_data["model"])
        
        print(f"Выбран блок: {block_data['id']}")

    def select_arrow(self, arrow_data):
        """Выбирает стрелку и обновляет панель свойств"""
        # Сбрасываем выделение предыдущей стрелки
        if self.selected_arrow:
            self.deselect_arrow()
        
        # Сбрасываем выделение блока, если был выбран
        if self.selected_block:
            self.canvas.itemconfig(self.selected_block["rect_id"], outline=Colors.TEXT_PRIMARY, width=2)
            self.delete_resize_handles(self.selected_block)
            self.selected_block = None
        
        # Выделяем новую стрелку
        self.selected_arrow = arrow_data
        arrow = arrow_data["arrow"]
        
        # Увеличиваем толщину линии для выделения
        if arrow_data.get("line_id"):
            self.canvas.itemconfig(arrow_data["line_id"], width=arrow.width + 2)
        
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
                if tag.startswith("arrow_") and tag != "arrow_line" and tag != "arrow_arrowhead":
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
            # Находим визуальное представление блока
            block_data = next((b for b in self.blocks if b["model"] == element), None)
            if block_data:
                # Обновляем визуальное представление
                if "name" in update_data:
                    self.canvas.itemconfig(block_data["text_id"], text=update_data["name"])
                
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
                    # Обновляем маркеры изменения размера
                    self.create_resize_handles(block_data)
                
                print(f"Обновлен блок {block_data['id']}: {update_data}")
        
        # Обработка стрелок
        elif isinstance(element, Arrow):
            # Находим визуальное представление стрелки
            arrow_data = next((a for a in self.arrows if a["arrow"] == element), None)
            if arrow_data:
                # Перерисовываем стрелку с новыми свойствами
                self.draw_arrow(arrow_data)
                
                # Если стрелка выбрана, обновляем выделение
                if self.selected_arrow == arrow_data:
                    arrow = arrow_data["arrow"]
                    if arrow_data.get("line_id"):
                        self.canvas.itemconfig(arrow_data["line_id"], width=arrow.width + 2)
            
            print(f"Обновлена стрелка {element.id}: {update_data}")

    def load_icon(self, name, size):
        """Загрузка PNG-иконки с безопасным фолбеком и кэшем.
        Поддерживает имена вида Name.png, Name (1).png, Name (2).png.
        """
        cache_key = f"{name}_{size[0]}x{size[1]}"
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
            img = Image.open(path).resize(size, Image.LANCZOS)
            self._icons[cache_key] = ImageTk.PhotoImage(img)
        except Exception:
            from PIL import Image as PILImage
            # Прозрачный фолбек нужного размера
            fallback = PILImage.new("RGBA", size, (0, 0, 0, 0))
            self._icons[cache_key] = ImageTk.PhotoImage(fallback)
        return self._icons[cache_key]

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

        # Canvas с прокруткой
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=Colors.SURFACE,
            highlightthickness=0,
            scrollregion=(-2000, -2000, 4000, 4000)  # Большая область для панорамирования
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

        # Привязка к событиям клавиатуры
        self.canvas.bind_all("<KeyPress-space>", self.on_space_press)
        self.canvas.bind_all("<KeyRelease-space>", self.on_space_release)

        # Обработчик клика по пустому месту для сброса выделения
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Обработчик движения мыши для превью стрелки
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Привязываем обработчики для выбора стрелок
        self.canvas.tag_bind("arrow_line", "<Button-1>", self.on_arrow_click)
        self.canvas.tag_bind("arrow_arrowhead", "<Button-1>", self.on_arrow_click)

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
                if "arrow_line" in tags or "arrow_arrowhead" in tags:
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
                    self.canvas.itemconfig(self.selected_block["rect_id"], outline=Colors.TEXT_PRIMARY, width=2)
                    self.delete_resize_handles(self.selected_block)
                    self.selected_block = None
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

    def apply_hover_effect(self, widget, base_bg, hover_bg):
        """Базовый ховер-эффект - только смена цвета"""
        def on_enter(_):
            widget.configure(bg=hover_bg)
        def on_leave(_):
            widget.configure(bg=base_bg)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def draw_grid(self):
        """Рисует сетку по всей области холста"""
        self.canvas.delete('grid')
        
        # Рисуем сетку на всей области scrollregion
        left, top, right, bottom = self.canvas.cget('scrollregion').split()
        left, top, right, bottom = int(left), int(top), int(right), int(bottom)

        # Minor grid (20px) - более светлая
        for i in range(left, right, 20):
            self.canvas.create_line(i, top, i, bottom, fill=Colors.GRID, width=1, tags='grid')
        for i in range(top, bottom, 20):
            self.canvas.create_line(left, i, right, i, fill=Colors.GRID, width=1, tags='grid')

        # Major grid (100px) - немного темнее
        for i in range(left, right, 100):
            self.canvas.create_line(i, top, i, bottom, fill=Colors.GRID_STRONG, width=1, tags='grid')
        for i in range(top, bottom, 100):
            self.canvas.create_line(left, i, right, i, fill=Colors.GRID_STRONG, width=1, tags='grid')
    
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
        
        # Удаляем старую линию, если существует
        if arrow_data.get("line_id"):
            try:
                self.canvas.delete(arrow_data["line_id"])
            except tk.TclError:
                pass  # Элемент уже удален
        
        # Рисуем линию стрелки (увеличиваем толщину если стрелка выбрана)
        line_width = arrow.width + 2 if (self.selected_arrow and arrow_data == self.selected_arrow) else arrow.width
        line_id = self.canvas.create_line(
            x1, y1, x2, y2,
            fill=arrow.color,
            width=line_width,
            dash=dash,
            tags=("arrow_line", arrow.id)
        )
        arrow_data["line_id"] = line_id
        
        # Удаляем старый наконечник, если существует
        if arrow_data.get("arrowhead_id"):
            try:
                self.canvas.delete(arrow_data["arrowhead_id"])
            except tk.TclError:
                pass  # Элемент уже удален
        
        # Рисуем наконечник стрелки
        arrowhead_id = self.create_arrowhead(x1, y1, x2, y2, arrow.color, arrow.width)
        arrow_data["arrowhead_id"] = arrowhead_id
        
        # Сохраняем ID для обновления
        if arrowhead_id:
            self.canvas.addtag_withtag(arrow.id, arrowhead_id)
        
        # Поднимаем стрелку наверх, чтобы она была поверх блоков
        self.canvas.tag_raise(line_id)
        if arrowhead_id:
            self.canvas.tag_raise(arrowhead_id)
        
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
            to_side=to_side
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
            y2=y
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
            y1=y
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
            y2=y2
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
            # Удаляем стрелки, соединенные с этим блоком
            block_id = self.selected_block["id"]
            arrows_to_remove = [a for a in self.arrows if a["arrow"].is_connected_to_block(block_id)]
            for arrow_data in arrows_to_remove:
                self.delete_arrow(arrow_data)
            
            # Удаляем блок
            self.canvas.delete(self.selected_block["rect_id"])
            self.canvas.delete(self.selected_block["text_id"])
            self.delete_resize_handles(self.selected_block)
            self.blocks.remove(self.selected_block)
            self.selected_block = None
            self.properties_panel.update_properties(None)
            print(f"Блок удален")
        elif self.selected_arrow:
            # Удаляем стрелку
            self.delete_arrow(self.selected_arrow)
            self.selected_arrow = None
            self.properties_panel.update_properties(None)
            print(f"Стрелка удалена")
    
    def delete_arrow(self, arrow_data):
        """Удаляет стрелку"""
        if arrow_data.get("line_id"):
            self.canvas.delete(arrow_data["line_id"])
        if arrow_data.get("arrowhead_id"):
            self.canvas.delete(arrow_data["arrowhead_id"])
        if arrow_data in self.arrows:
            self.arrows.remove(arrow_data)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
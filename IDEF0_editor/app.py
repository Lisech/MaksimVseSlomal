"""
Чистый макет приложения - точная копия HTML макета
Все кнопки с заглушками
"""

import tkinter as tk
from tkinter import ttk
import os
from styles import Colors, Dimensions, Fonts
from properties import PropertiesPanel
from PIL import Image, ImageTk
from models import Block

class IDEF0App:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        self.blocks = []
        self.next_block_id = 1
        self.is_panning = False  # флаг режима панорамирования
    
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
        properties_panel = PropertiesPanel(main_frame)
        properties_panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))

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
                btn.configure(command=self.disable_pan_mode)

            if icon_name == "Hand":
                btn.configure(command=self.enable_pan_mode)

            # Привязываем обработчик для кнопки добавления блока
            if icon_name == "Square":
                btn.configure(command=self.add_new_block)

            self.apply_hover_effect(btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")
            btn.pack(pady=8)

    def add_new_block(self):
        """Добавляет новый блок на холст с базовыми значениями"""
        # Базовые координаты (центр видимой области)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x = canvas_width // 2 if canvas_width > 0 else 400
        y = canvas_height // 2 if canvas_height > 0 else 300

        # Базовые размеры
        width, height = 150, 80

        # Создаем блок
        block_id = f"block_{self.next_block_id}"
        self.next_block_id += 1

        # Рисуем прямоугольник
        rect = self.canvas.create_rectangle(
            x - width / 2, y - height / 2,
            x + width / 2, y + height / 2,
            fill="#E3F2FD",  # голубой цвет как в models.py
            outline=Colors.TEXT_PRIMARY,
            width=2,
            tags=("block", block_id)
        )

        # Добавляем текст
        text = self.canvas.create_text(
            x, y,
            text=f"Блок {self.next_block_id - 1}",
            font=("Segoe UI", 10),
            justify="center",
            tags=("block_text", block_id)
        )

        # Сохраняем информацию о блоке
        block_data = {
            "id": block_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "rect_id": rect,
            "text_id": text,
            "name": f"Блок {self.next_block_id - 1}",
            "color": "#E3F2FD"
        }

        self.blocks.append(block_data)

        # Делаем блок перемещаемым
        self.make_block_draggable(block_data)

        print(f"Добавлен новый блок: {block_id}")
        print(f"Всего блоков: {len(self.blocks)}")

    def make_block_draggable(self, block_data):
        """Делает блок перемещаемым по холсту"""

        def start_drag(event):
            # Запоминаем начальные координаты
            if self.is_panning == False:
                block_data["drag_data"] = {"x": event.x, "y": event.y}

        def drag(event):
            if "drag_data" in block_data:
                # Вычисляем смещение
                dx = event.x - block_data["drag_data"]["x"]
                dy = event.y - block_data["drag_data"]["y"]

                # Обновляем позицию блока
                block_data["x"] += dx
                block_data["y"] += dy

                # Перемещаем прямоугольник и текст
                self.canvas.move(block_data["rect_id"], dx, dy)
                self.canvas.move(block_data["text_id"], dx, dy)

                # Обновляем данные о перетаскивании
                block_data["drag_data"] = {"x": event.x, "y": event.y}

        def end_drag(event):
            if "drag_data" in block_data:
                del block_data["drag_data"]
                print(f"Блок {block_data['id']} перемещен в ({block_data['x']:.1f}, {block_data['y']:.1f})")

        # Привязываем обработчики событий
        self.canvas.tag_bind(block_data["rect_id"], "<ButtonPress-1>", start_drag)
        self.canvas.tag_bind(block_data["rect_id"], "<B1-Motion>", drag)
        self.canvas.tag_bind(block_data["rect_id"], "<ButtonRelease-1>", end_drag)

        self.canvas.tag_bind(block_data["text_id"], "<ButtonPress-1>", start_drag)
        self.canvas.tag_bind(block_data["text_id"], "<B1-Motion>", drag)
        self.canvas.tag_bind(block_data["text_id"], "<ButtonRelease-1>", end_drag)

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

        # Canvas
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=Colors.SURFACE,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Перерисовывать сетку при изменении размера канвы
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Draw only grid (убран тестовый элемент на сетке)
        self.draw_grid()

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
        self.canvas.bind_all("<KeyPress-space>", self.enable_pan_mode)
        self.canvas.bind_all("<KeyRelease-space>", self.disable_pan_mode)

    def enable_pan_mode(self, event=None):
        """Включает режим панорамирования при нажатии пробела"""
        if not self.is_panning:
            self.is_panning = True
            self.canvas.configure(cursor="hand2")
            
            self.canvas.bind("<ButtonPress-1>", self.pan_start)
            self.canvas.bind("<B1-Motion>", self.pan_move)
            self.canvas.bind("<ButtonRelease-1>", self.pan_end)
            print(f"вошел в режим панорамирование")
    
    def disable_pan_mode(self, event=None):
        """Отключает режим панорамирования при отпускании пробела"""
        if self.is_panning:
            self.is_panning = False
            self.canvas.configure(cursor="")
            
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            print(f"вышел из режима панорамирование")

    def pan_start(self, event):
        """Запоминаем точку начала панорамирования"""
        self.canvas.scan_mark(event.x, event.y)

    def pan_move(self, event):
        """Перемещаем холст"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def pan_end(self, event):
        """Финализируем перемещение"""
        pass

    def apply_hover_effect(self, widget, base_bg, hover_bg):
        """Базовый ховер-эффект - только смена цвета"""
        def on_enter(_):
            widget.configure(bg=hover_bg)
        def on_leave(_):
            widget.configure(bg=base_bg)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def draw_grid(self):
        """Рисует сетку по текущему размеру канвы"""
        self.canvas.delete('grid')
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)

        # Minor grid (20px) - более светлая
        for i in range(0, width, 20):
            self.canvas.create_line(i, 0, i, height, fill=Colors.GRID, width=1, tags='grid')
        for i in range(0, height, 20):
            self.canvas.create_line(0, i, width, i, fill=Colors.GRID, width=1, tags='grid')

        # Major grid (100px) - немного темнее
        for i in range(0, width, 100):
            self.canvas.create_line(i, 0, i, height, fill=Colors.GRID_STRONG, width=1, tags='grid')
        for i in range(0, height, 100):
            self.canvas.create_line(0, i, width, i, fill=Colors.GRID_STRONG, width=1, tags='grid')

    def on_canvas_resize(self, _event):
        """Обработчик изменения размера канвы: перерасчёт сетки."""
        self.draw_grid()

    def draw_a0_block(self):
        """Рисует центральный A0 блок"""
        x, y = 400, 300
        width, height = 150, 80

        # Main block
        self.canvas.create_rectangle(
            x - width/2, y - height/2,
            x + width/2, y + height/2,
            fill=Colors.SURFACE,
            outline=Colors.TEXT_PRIMARY,
            width=2
        )

        # Text
        self.canvas.create_text(
            x, y,
            text="Основная\nдеятельность",
            font=("Segoe UI", 10),
            justify="center"
        )

    def draw_labels_and_arrows(self):
        """Рисует метки и стрелки вокруг A0 блока"""
        x, y = 400, 300
        width, height = 150, 80

        # Labels
        labels = [
            (x, y - height/2 - 20, "Управление", "top"),
            (x - width/2 - 28, y, "Вход", "left"),
            (x, y + height/2 + 20, "Механизм", "bottom"),
            (x + width/2 + 42, y, ">Выход", "right"),
            (x + width/2 + 10, y + height/2 + 16, "A0", "a0")
        ]

        for label_x, label_y, text, position in labels:
            angle = 0
            if position == "left":
                angle = 90

            self.canvas.create_text(
                label_x, label_y,
                text=text,
                font=("Segoe UI", 9),
                fill=Colors.TEXT_SECONDARY,
                angle=angle
            )

        # Right arrow
        arrow_start_x = x + width/2
        arrow_end_x = x + width/2 + 34

        self.canvas.create_line(
            arrow_start_x, y,
            arrow_end_x, y,
            fill=Colors.TEXT_PRIMARY,
            width=2
        )

        # Arrow head
        self.canvas.create_polygon(
            arrow_end_x, y,
            arrow_end_x - 8, y - 6,
            arrow_end_x - 8, y + 6,
            fill=Colors.TEXT_PRIMARY,
            outline=Colors.TEXT_PRIMARY
        )
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
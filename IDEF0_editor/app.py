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
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.selected_block = None  # текущий выбранный блок
        self.dragging_block = None  # блок, который сейчас перетаскивается
        self.current_mode = "select"  # режим работы: "select" или "pan"
    
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

            # Привязываем обработчик для кнопки добавления блока
            if icon_name == "Square":
                btn.configure(command=self.add_new_block)

            self.apply_hover_effect(btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")
            btn.pack(pady=8)

    def enable_select_mode(self):
        """Включает режим выбора элементов"""
        if self.current_mode != "select":
            self.current_mode = "select"
            self.is_panning = False
            self.canvas.configure(cursor="")
            print("Включен режим выбора")

    def enable_pan_mode(self):
        """Включает режим панорамирования"""
        if self.current_mode != "pan":
            self.current_mode = "pan"
            self.is_panning = True
            self.canvas.configure(cursor="hand2")
            print("Включен режим панорамирования")

    def add_new_block(self):
        """Добавляет новый блок на холст с базовыми значениями"""
        # Получаем видимую область холста
        canvas_x = self.canvas.canvasx(0)
        canvas_y = self.canvas.canvasy(0)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x = canvas_x + canvas_width // 2 if canvas_width > 0 else 400
        y = canvas_y + canvas_height // 2 if canvas_height > 0 else 300

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
            width=2,
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
            "text_id": text
        }

        self.blocks.append(block_data)

        # Делаем блок перемещаемым и выбираемым
        self.make_block_interactive(block_data)

        # Автоматически выбираем новый блок
        self.select_block(block_data)

        print(f"Добавлен новый блок: {block_id}")
        print(f"Всего блоков: {len(self.blocks)}")

    def make_block_interactive(self, block_data):
        """Делает блок перемещаемым по холсту и выбираемым"""
        def start_drag(event):
            if self.current_mode == "select":
                # Преобразуем координаты мыши в координаты холста
                x = self.canvas.canvasx(event.x)
                y = self.canvas.canvasy(event.y)
                block_data["drag_data"] = {"x": x, "y": y}
                self.dragging_block = block_data
                # Останавливаем распространение события
                return "break"

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

                # Обновляем данные о перетаскивании
                block_data["drag_data"] = {"x": x, "y": y}

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

        # Привязываем обработчики событий
        for item_id in [block_data["rect_id"], block_data["text_id"]]:
            self.canvas.tag_bind(item_id, "<ButtonPress-1>", start_drag)
            self.canvas.tag_bind(item_id, "<B1-Motion>", drag)
            self.canvas.tag_bind(item_id, "<ButtonRelease-1>", end_drag)
            self.canvas.tag_bind(item_id, "<Double-Button-1>", double_click)

    def select_block(self, block_data):
        """Выбирает блок и обновляет панель свойств"""
        # Сбрасываем выделение предыдущего блока
        if self.selected_block:
            self.canvas.itemconfig(self.selected_block["rect_id"], outline=Colors.TEXT_PRIMARY, width=2)
        
        # Выделяем новый блок
        self.selected_block = block_data
        self.canvas.itemconfig(block_data["rect_id"], outline=Colors.PRIMARY, width=3)
        
        # Обновляем панель свойств
        self.properties_panel.update_properties(block_data["model"])
        
        print(f"Выбран блок: {block_data['id']}")

    def on_properties_change(self, block, update_data):
        """Обработчик изменений в свойствах блока"""
        # Обновляем модель блока
        block.update_from_dict(update_data)
        
        # Находим визуальное представление блока
        block_data = next((b for b in self.blocks if b["model"] == block), None)
        if block_data:
            # Обновляем визуальное представление
            if "name" in update_data:
                self.canvas.itemconfig(block_data["text_id"], text=update_data["name"])
            
            if "color" in update_data:
                self.canvas.itemconfig(block_data["rect_id"], fill=update_data["color"])
            
            if any(key in update_data for key in ["x", "y", "width", "height"]):
                # Перерисовываем блок с новыми размерами/позицией
                x1 = block.x - block.width / 2
                y1 = block.y - block.height / 2
                x2 = block.x + block.width / 2
                y2 = block.y + block.height / 2
                
                self.canvas.coords(block_data["rect_id"], x1, y1, x2, y2)
                self.canvas.coords(block_data["text_id"], block.x, block.y)
            
            # ВАЖНО: Обновляем обводку выбранного элемента
            if self.selected_block == block_data:
                # Устанавливаем выделенную обводку для выбранного элемента
                self.canvas.itemconfig(block_data["rect_id"], outline=Colors.PRIMARY, width=3)
            
        print(f"Обновлен блок {block_data['id']}: {update_data}")

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
        else:
            # Если не панорамирование, проверяем клик по блоку
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            block_clicked = False
            for item in items:
                tags = self.canvas.gettags(item)
                if "block" in tags:
                    block_clicked = True
                    break
            
            # Если клик был не по блоку - сбрасываем выделение
            if not block_clicked:
                if self.selected_block:
                    self.canvas.itemconfig(self.selected_block["rect_id"], outline=Colors.TEXT_PRIMARY, width=2)
                    self.selected_block = None
                    self.properties_panel.update_properties(None)
                    print("Сброс выделения")

    def on_canvas_release(self, event):
        """Обработчик отпускания кнопки мыши на холсте"""
        # Сбрасываем перетаскиваемый блок
        self.dragging_block = None

    def pan_start(self, event):
        """Запоминаем точку начала панорамирования"""
        self.canvas.scan_mark(event.x, event.y)

    def pan_move(self, event):
        """Перемещаем холст"""
        if self.is_panning:
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
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
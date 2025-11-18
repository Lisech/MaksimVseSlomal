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
from models import LayerManager

class IDEF0App:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.current_right_panel = "properties"  # или "layers"
        self.layers_panel_visible = False
        self.layers_panel = None
        
        self.setup_ui()
        self.blocks = []
        self.next_block_id = 1
        self.is_panning = False  # флаг режима панорамирования
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.selected_block = None  # текущий выбранный блок
        self.dragging_block = None  # блок, который сейчас перетаскивается
        self.current_mode = "select"  # режим работы: "select" или "pan"
        self.drag_from_sidebar = False  # флаг перетаскивания из панели
        self.drag_preview = None  # превью перетаскиваемого блока
        self.resizing_block = None  # блок, который сейчас изменяется
        self.resize_handle_size = 8  # размер маркеров изменения размера
        self.resize_preview = None  # превью растягивания
        self.layer_manager = LayerManager()
        self.level_states = {}
    
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

        # Properties panel (по умолчанию видна)
        self.properties_panel = PropertiesPanel(main_frame, on_properties_change=self.on_properties_change)
        self.properties_panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))

        # Панель слоев (изначально скрыта)
        self.setup_layers_panel(main_frame)

        # Переменная для отслеживания текущей панели
        self.current_right_panel = "properties"  # или "layers"

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
        self.apply_hover_effect(close_btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")

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

    def show_layers_panel(self):
        """Показывает панель слоев вместо свойств"""
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
        # Убираем проверку условия - всегда показываем свойства при нажатии на крестик
        # Скрываем слои
        self.layers_panel_frame.grid_remove()
        
        # Показываем свойства
        self.properties_panel.grid()
        
        self.current_right_panel = "properties"
        self.layers_panel_visible = False
        print("Панель свойств открыта")

    def hide_layers_panel(self):
        """Скрывает панель слоев"""
        self.layers_panel_frame.grid_remove()
        self.layers_panel_visible = False

    def update_layers_tree(self):
        """Обновляет дерево слоев"""
        # Очищаем текущее дерево
        for item in self.layers_tree.get_children():
            self.layers_tree.delete(item)

        # Строим иерархию
        hierarchy = self.layer_manager.build_hierarchy_tree([b["model"] for b in self.blocks])
        
        # Добавляем корневой уровень (более лаконичное название)
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
        for child_data in children:
            block = child_data['block']
            
            # ИСПРАВЛЕНИЕ: отображаем только код блока, без названия
            item_text = f"{block.code}"  # Только код
            
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
                block_code = self.layers_tree.item(item, "text")  # Получаем код блока для отладки
                
                print(f"Двойной клик на блоке {block_code} (id: {block_id})")
                
                # ПЕРЕХОДИМ НА УРОВЕНЬ БЛОКА
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
            ("Layers", "Показать слои"),
            ("ChevronUp", "Слой вверх"),
            ("ChevronDown", "Слой вниз"),
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

            if icon_name == "Square":
                btn.configure(command=None)
                btn.bind("<ButtonPress-1>", self.start_drag_from_sidebar)
                btn.bind("<B1-Motion>", self.drag_from_sidebar)
                btn.bind("<ButtonRelease-1>", self.end_drag_from_sidebar)

            # Кнопка "Layers" - переключает между свойствами и слоями
            if icon_name == "Layers":
                if self.current_right_panel == "properties":
                    btn.configure(command=self.show_layers_panel)
                else:
                    btn.configure(command=self.show_properties_panel)

            if icon_name == "ChevronUp":
                btn.configure(command=self.level_up)

            if icon_name == "ChevronDown":
                btn.configure(command=self.level_down)

            self.apply_hover_effect(btn, base_bg=Colors.SURFACE, hover_bg="#e2e8f0")
            btn.pack(pady=8)
        

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
        
        self.update_footer_info()
        print(f"Перешли на уровень детализации блока {self.selected_block['model'].code}")

    def level_up(self):
        """Возврат на уровень выше"""
        if self.layer_manager.exit_level():
            # Восстанавливаем состояние предыдущего уровня
            level_key = self.layer_manager.get_current_level_key()
            self.restore_level_state(level_key)
            self.update_footer_info()
            print(f"Вернулись на уровень выше")
        else:
            print("Уже на корневом уровне")

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

    def show_layers_panel(self):
        """Показывает панель слоев"""
        if not self.layers_panel_visible:
            self.layers_panel_frame.grid()
            self.update_layers_tree()  # ОБНОВЛЯЕМ ДЕРЕВО ПРИ ОТКРЫТИИ
            self.layers_panel_visible = True
            print("Панель слоев открыта")
        else:
            self.hide_layers_panel()

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
            outline=Colors.TEXT_PRIMARY,
            width=model.border_width,
            tags=("block", block_data["id"])
        )

        # Добавляем основной текст
        text = self.canvas.create_text(
            model.x, model.y,
            text=model.name,
            font=("Segoe UI", 10),
            justify="center",
            tags=("block_text", block_data["id"])
        )

        # Добавляем код в правом нижнем углу
        code_x, code_y = model.get_code_position()
        code_text = self.canvas.create_text(
            code_x, code_y,
            text=model.code,
            font=("Segoe UI", 8),
            fill="#666666",
            anchor="se",
            tags=("block_code", block_data["id"])
        )

        # Обновляем ID элементов в блоке
        block_data["rect_id"] = rect
        block_data["text_id"] = text
        block_data["code_text_id"] = code_text

        # Делаем блок интерактивным
        self.make_block_interactive(block_data)

    def update_footer_info(self):
        """Обновляет информацию в футере о текущем уровне"""
        level_path = self.layer_manager.get_level_path([b["model"] for b in self.blocks])
        
        # Обновляем левый лейбл (диаграмма и масштаб)
        self.footer_left_label.config(text="Диаграмма: Пример IDEF0 | Масштаб: 100%")
        
        # Обновляем правый лейбл (уровень)
        self.footer_right_label.config(text=level_path)

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
            parent_block = next((b["model"] for b in self.blocks if b["id"] == parent_id), None)
            if parent_block:
                # Считаем сколько уже есть блоков на этом уровне с тем же родителем
                sibling_blocks = [b for b in self.blocks if b["model"].parent_id == parent_id]
                code = f"{parent_block.code}.{len(sibling_blocks) + 1}"
            else:
                code = f"A{len(current_blocks) + 1}"
        else:
            # Корневой уровень
            code = f"A{len(current_blocks) + 1}"

        # Создаем модель блока
        block_model = Block(
            block_id=block_id,
            name=f"Блок {code}",
            code=code,
            x=x,
            y=y,
            width=width,
            height=height,
            parent_id=parent_id,
            level=len(self.layer_manager.current_level_path)  # Уровень = глубина вложенности
        )

        # Используем общий метод для создания визуального представления
        self.create_visual_block(block_model)

        # Автоматически выбираем новый блок
        block_data = next((b for b in self.blocks if b["id"] == block_id), None)
        if block_data:
            self.select_block(block_data)

        print(f"Добавлен новый блок: {block_id} (Родитель: {parent_id}, Код: {code})")
        print(f"Всего блоков: {len(self.blocks)}")

    def create_visual_block(self, block_model):
        """Создает визуальное представление блока на холсте"""
        # Рисуем прямоугольник
        rect = self.canvas.create_rectangle(
            block_model.x - block_model.width / 2, block_model.y - block_model.height / 2,
            block_model.x + block_model.width / 2, block_model.y + block_model.height / 2,
            fill=block_model.color,
            outline=Colors.TEXT_PRIMARY,
            width=block_model.border_width,
            tags=("block", block_model.id)
        )

        # Добавляем основной текст
        text = self.canvas.create_text(
            block_model.x, block_model.y,
            text=block_model.name,
            font=("Segoe UI", 10),
            justify="center",
            tags=("block_text", block_model.id)
        )

        # Добавляем код в правом нижнем углу
        code_x, code_y = block_model.get_code_position()
        code_text = self.canvas.create_text(
            code_x, code_y,
            text=block_model.code,
            font=("Segoe UI", 8),
            fill="#666666",
            anchor="se",
            tags=("block_code", block_model.id)
        )

        # Сохраняем информацию о блоке
        block_data = {
            "id": block_model.id,
            "model": block_model,
            "rect_id": rect,
            "text_id": text,
            "code_text_id": code_text,
            "resize_handles": {}
        }

        self.blocks.append(block_data)

        # Делаем блок перемещаемым и выбираемым
        self.make_block_interactive(block_data)
        
        print(f"Создан дочерний блок: {block_model.code}")

    def enable_select_mode(self):
        """Включает режим выбора элементов"""
        if self.current_mode != "select":
            self.current_mode = "select"
            self.is_panning = False
            self.canvas.configure(cursor="")
            print("Включен режим выбора")
            self.restore_block_handlers()

    def enable_pan_mode(self):
        """Включает режим панорамирования"""
        if self.current_mode != "pan":
            self.current_mode = "pan"
            self.is_panning = True
            self.canvas.configure(cursor="hand2")
            print("Включен режим панорамирования")
            self.disable_block_handlers()

    def restore_block_handlers(self):
        """Восстанавливает обработчики событий для всех блоков"""
        for block_data in self.blocks:
            self.make_block_interactive(block_data)

    def disable_block_handlers(self):
        """Отключает обработчики событий для всех блоков в режиме панорамирования"""
        for block_data in self.blocks:
            for item_id in [block_data["rect_id"], block_data["text_id"]]:
                # Удаляем все привязанные обработчики
                self.canvas.tag_unbind(item_id, "<ButtonPress-1>")
                self.canvas.tag_unbind(item_id, "<B1-Motion>")
                self.canvas.tag_unbind(item_id, "<ButtonRelease-1>")
                self.canvas.tag_unbind(item_id, "<Double-Button-1>")

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
            
            # Обновляем визуальное представление блока (включая код)
            self.update_block_visual(block_data)
            
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
        
        # Обновляем основной текст
        self.canvas.coords(block_data["text_id"], model.x, model.y)
        
        # Обновляем позицию кода (абсолютные координаты)
        code_x, code_y = model.get_code_position()
        self.canvas.coords(block_data["code_text_id"], code_x, code_y)
        
        # Обновляем маркеры изменения размера
        if block_data == self.selected_block:
            self.create_resize_handles(block_data)

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
                not self.is_panning and
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

                # Перемещаем ВСЕ элементы блока
                self.canvas.move(block_data["rect_id"], dx, dy)
                self.canvas.move(block_data["text_id"], dx, dy)
                self.canvas.move(block_data["code_text_id"], dx, dy)  # Добавляем перемещение кода

                # Обновляем маркеры изменения размера
                if block_data == self.selected_block:
                    for handle_id in block_data["resize_handles"].values():
                        self.canvas.move(handle_id, dx, dy)

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
        for item_id in [block_data["rect_id"], block_data["text_id"], block_data["code_text_id"]]:
            self.canvas.tag_unbind(item_id, "<ButtonPress-1>")
            self.canvas.tag_unbind(item_id, "<B1-Motion>")
            self.canvas.tag_unbind(item_id, "<ButtonRelease-1>")
            self.canvas.tag_unbind(item_id, "<Double-Button-1>")

        # Привязываем новые обработчики событий ко всем элементам блока
        for item_id in [block_data["rect_id"], block_data["text_id"], block_data["code_text_id"]]:
            self.canvas.tag_bind(item_id, "<ButtonPress-1>", start_drag)
            self.canvas.tag_bind(item_id, "<B1-Motion>", drag)
            self.canvas.tag_bind(item_id, "<ButtonRelease-1>", end_drag)
            self.canvas.tag_bind(item_id, "<Double-Button-1>", double_click)

    def select_block(self, block_data):
        """Выбирает блок и обновляет панель свойств (только если блок на текущем уровне)"""
        # Проверяем, принадлежит ли блок текущему уровню
        current_blocks_models = self.layer_manager.get_blocks_for_current_level([b["model"] for b in self.blocks])
        current_blocks_ids = [block.id for block in current_blocks_models]
        
        if block_data["model"].id not in current_blocks_ids:
            print(f"Блок {block_data['model'].code} не принадлежит текущему уровню")
            return
        
        # Сбрасываем выделение предыдущего блока
        if self.selected_block:
            self.canvas.itemconfig(self.selected_block["rect_id"], outline=Colors.TEXT_PRIMARY, width=self.selected_block["model"].border_width)
            self.delete_resize_handles(self.selected_block)
        
        # Выделяем новый блок
        self.selected_block = block_data
        self.canvas.itemconfig(block_data["rect_id"], outline=Colors.PRIMARY, width=block_data["model"].border_width + 1)
        
        # Создаем маркеры изменения размера
        self.create_resize_handles(block_data)
        
        # Обновляем панель свойств и автоматически переключаем на нее
        self.properties_panel.update_properties(block_data["model"])
        self.show_properties_panel()
        
        print(f"Выбран блок: {block_data['id']} ({block_data['model'].code})")

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
            
            if "code" in update_data:
                # Обновляем текст кода
                self.canvas.itemconfig(block_data["code_text_id"], text=update_data["code"])
                # Обновляем позицию кода (на случай изменения размера)
                code_x, code_y = block.get_code_position()
                self.canvas.coords(block_data["code_text_id"], code_x, code_y)
            
            if "color" in update_data:
                self.canvas.itemconfig(block_data["rect_id"], fill=update_data["color"])
            
            if "border_width" in update_data:
                self.canvas.itemconfig(block_data["rect_id"], width=update_data["border_width"])
            
            if any(key in update_data for key in ["x", "y", "width", "height"]):
                self.update_block_visual(block_data)
            
            # ВАЖНО: Обновляем обводку выбранного элемента
            if self.selected_block == block_data:
                # Устанавливаем выделенную обводку для выбранного элемента
                self.canvas.itemconfig(block_data["rect_id"], outline=Colors.PRIMARY, width=block.border_width)
                # Обновляем маркеры изменения размера
                self.create_resize_handles(block_data)
        
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

        self.footer_right_label = tk.Label(
            canvas_frame,
            text="Уровень 0",
            font=("Segoe UI", 9),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.SURFACE
        )
        self.footer_right_label.place(relx=1, rely=1, x=-14, y=-10, anchor='se')
        # Привязка к событиям клавиатуры
        self.canvas.bind_all("<KeyPress-space>", self.on_space_press)
        self.canvas.bind_all("<KeyRelease-space>", self.on_space_release)

        # Обработчик клика по пустому месту для сброса выделения
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<B1-Motion>", self.pan_move)

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
        if self.is_panning or self.current_mode == "pan":
            # Если включено панорамирование (пробел зажат или режим панорамирования), начинаем панорамирование
            self.canvas.scan_mark(event.x, event.y)
            return  # Прерываем дальнейшую обработку
        
        # Преобразуем координаты мыши в координаты холста
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Если не панорамирование, проверяем клик по блоку или маркеру
        items = self.canvas.find_overlapping(x, y, x, y)
        block_or_handle_clicked = False
        
        for item in items:
            tags = self.canvas.gettags(item)
            if "block" in tags or "resize_handle" in tags:
                block_or_handle_clicked = True
                break
        
        # Если клик был не по блоку или маркеру - сбрасываем выделение
        if not block_or_handle_clicked:
            if self.selected_block:
                self.canvas.itemconfig(self.selected_block["rect_id"], 
                                    outline=Colors.TEXT_PRIMARY, 
                                    width=self.selected_block["model"].border_width)
                self.delete_resize_handles(self.selected_block)
                self.selected_block = None
                self.properties_panel.update_properties(None)
                print("Сброс выделения")

    def on_canvas_release(self, event):
        """Обработчик отпускания кнопки мыши на холсте"""
        # Сбрасываем перетаскиваемый блок
        self.dragging_block = None
        # Сбрасываем изменение размера
        self.resizing_block = None
        
        # Если был режим панорамирования и он временный (по пробелу), возвращаем курсор
        if self.current_mode == "select" and self.is_panning:
            self.canvas.configure(cursor="")
            self.is_panning = False

    def pan_move(self, event):
        """Перемещаем холст"""
        if self.is_panning or self.current_mode == "pan":
            self.canvas.scan_dragto(event.x, event.y, gain=1)

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
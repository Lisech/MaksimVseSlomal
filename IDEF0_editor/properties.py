"""
Панель свойств - динамическое обновление свойств выбранного элемента
"""

import tkinter as tk
from styles import Colors, Dimensions, Fonts
from models import Block, Arrow

class PropertiesPanel(tk.Frame):
    def __init__(self, parent, on_properties_change=None):
        super().__init__(parent, bg=Colors.BACKGROUND, width=Dimensions.PROPERTIES_WIDTH)
        self.pack_propagate(False)
        
        # Колбэк для уведомления об изменениях
        self.on_properties_change = on_properties_change
        
        # Текущий выбранный элемент
        self.current_block = None
        
        # Ссылки на виджеты для обновления
        self.fields = {}
        
        # Текущая толщина границы
        self.current_border_width = 2
        self.current_arrow_width = 2
        
        self.setup_ui()

    def setup_ui(self):
        # Основной контейнер с прокруткой
        canvas = tk.Canvas(self, bg=Colors.BACKGROUND, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BACKGROUND)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Основной контейнер для карточек
        content_frame = scrollable_frame
        
        # Карточка свойств элемента (для блоков)
        self.element_properties_card = self.create_card(content_frame, "Свойства элемента")
        self.create_element_properties(self.element_properties_card)
        self.element_properties_card.card_outer.pack(fill=tk.X, pady=(0, 16))

        # Карточка позиции и размера (для блоков)
        self.position_card = self.create_card(content_frame, "Позиция и размер")
        self.create_position_card(self.position_card)
        self.position_card.card_outer.pack(fill=tk.X, pady=(0, 16))

        # Карточка стиля (для блоков)
        self.style_card = self.create_card(content_frame, "Стиль")
        self.create_style_card(self.style_card)
        self.style_card.card_outer.pack(fill=tk.X, pady=(0, 16))
        
        # Карточка свойств стрелки (для стрелок)
        self.arrow_properties_card = self.create_card(content_frame, "Свойства стрелки")
        self.create_arrow_properties(self.arrow_properties_card)
        # Скрываем карточку стрелок по умолчанию
        self.arrow_properties_card.card_outer.pack_forget()
        
        # Привязка прокрутки колесиком мыши
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def create_element_properties(self, parent):
        """Карточка 'Свойства элемента'"""
        # Поле Название
        self.create_field(parent, "Название", "name", "Введите название...")

        # Поле Код
        self.create_field(parent, "Код", "code", "A0")

        # Поле Тип элемента
        self.create_select_field(parent, "Тип элемента", "element_type", 
                               ["Выберите тип", "Процесс", "Функция", "Действие", "Операция"])

        # Поле Описание
        self.create_field(parent, "Описание", "description", "Введите описание элемента...")

    def create_position_card(self, parent):
        """Карточка 'Позиция и размер'"""
        # Строка X, Y
        row1 = tk.Frame(parent, bg=Colors.SURFACE)
        row1.pack(fill=tk.X, padx=14, pady=(0, 12))

        self.create_small_field(row1, "X", "x", "100", 0)
        self.create_small_field(row1, "Y", "y", "150", 1)

        # Строка Ширина, Высота
        row2 = tk.Frame(parent, bg=Colors.SURFACE)
        row2.pack(fill=tk.X, padx=14)

        self.create_small_field(row2, "Ширина", "width", "150", 0)
        self.create_small_field(row2, "Высота", "height", "80", 1)

    def create_style_card(self, parent):
        """Карточка 'Стиль'"""
        # Цвет заливки
        color_frame = tk.Frame(parent, bg=Colors.SURFACE)
        color_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            color_frame,
            text="Цвет заливки",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Цветовые образцы
        colors_frame = tk.Frame(color_frame, bg=Colors.SURFACE)
        colors_frame.pack(fill=tk.X, padx=14, pady=(5, 0))

        colors = [
            ("#cfe8ff", "blue"),
            ("#d9f4d0", "green"),
            ("#fff5c2", "yellow"),
            ("#ffffff", "white"),
            ("#E3F2FD", "light_blue"),  # текущий цвет по умолчанию
            ("#ffd6cc", "orange"),
            ("#e6ccff", "purple")
        ]

        self.color_swatches = {}
        for color, name in colors:
            swatch_frame = tk.Frame(colors_frame, bg=Colors.SURFACE)
            swatch_frame.pack(side=tk.LEFT, padx=(0, 10), pady=2)
            
            swatch = tk.Frame(
                swatch_frame,
                bg=color,
                width=30,
                height=24,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=Colors.BORDER
            )
            swatch.pack()
            swatch.pack_propagate(False)
            
            # Привязываем обработчик клика
            swatch.bind("<Button-1>", lambda e, c=color: self.on_color_selected(c))
            self.color_swatches[color] = swatch

        # Толщина границы
        border_frame = tk.Frame(parent, bg=Colors.SURFACE)
        border_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        tk.Label(
            border_frame,
            text="Толщина границы",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Контейнер для элементов управления толщиной
        border_controls_frame = tk.Frame(border_frame, bg=Colors.SURFACE)
        border_controls_frame.pack(fill=tk.X, pady=(5, 0))

        # Кнопка уменьшения
        self.border_minus_btn = tk.Button(
            border_controls_frame,
            text="-",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            width=3,
            height=1,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=lambda: self.change_border_width(-1)
        )
        self.border_minus_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.apply_hover_effect(self.border_minus_btn)

        # Отображение текущей толщины
        self.border_width_label = tk.Label(
            border_controls_frame,
            text="2px",
            font=("Segoe UI", 11),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            width=6
        )
        self.border_width_label.pack(side=tk.LEFT, padx=4)

        # Кнопка увеличения
        self.border_plus_btn = tk.Button(
            border_controls_frame,
            text="+",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            width=3,
            height=1,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=lambda: self.change_border_width(1)
        )
        self.border_plus_btn.pack(side=tk.LEFT, padx=(8, 0))
        self.apply_hover_effect(self.border_plus_btn)
    
    def create_arrow_properties(self, parent):
        """Карточка 'Свойства стрелки'"""
        # Цвет стрелки
        color_frame = tk.Frame(parent, bg=Colors.SURFACE)
        color_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            color_frame,
            text="Цвет стрелки",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Цветовые образцы для стрелок
        colors_frame = tk.Frame(color_frame, bg=Colors.SURFACE)
        colors_frame.pack(fill=tk.X, padx=14, pady=(5, 0))

        arrow_colors = [
            ("#cfe8ff", "blue"),
            ("#d9f4d0", "green"),
            ("#fff5c2", "yellow"),
            ("#000000", "black"),
            ("#E3F2FD", "light_blue"),  # текущий цвет по умолчанию
            ("#ffd6cc", "orange"),
            ("#e6ccff", "purple")
        ]

        self.arrow_color_swatches = {}
        for color, name in arrow_colors:
            swatch_frame = tk.Frame(colors_frame, bg=Colors.SURFACE)
            swatch_frame.pack(side=tk.LEFT, padx=(0, 10), pady=2)
            
            swatch = tk.Frame(
                swatch_frame,
                bg=color,
                width=30,
                height=24,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=Colors.BORDER
            )
            swatch.pack()
            swatch.pack_propagate(False)
            
            # Привязываем обработчик клика
            swatch.bind("<Button-1>", lambda e, c=color: self.on_arrow_color_selected(c))
            self.arrow_color_swatches[color] = swatch

        # Толщина стрелки
        width_frame = tk.Frame(parent, bg=Colors.SURFACE)
        width_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        tk.Label(
            width_frame,
            text="Толщина стрелки",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Контейнер для элементов управления толщиной
        width_controls_frame = tk.Frame(width_frame, bg=Colors.SURFACE)
        width_controls_frame.pack(fill=tk.X, pady=(5, 0))

        # Кнопка уменьшения
        self.arrow_width_minus_btn = tk.Button(
            width_controls_frame,
            text="-",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            width=3,
            height=1,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=lambda: self.change_arrow_width(-1)
        )
        self.arrow_width_minus_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.apply_hover_effect(self.arrow_width_minus_btn)

        # Отображение текущей толщины
        self.arrow_width_label = tk.Label(
            width_controls_frame,
            text="2px",
            font=("Segoe UI", 11),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            width=6
        )
        self.arrow_width_label.pack(side=tk.LEFT, padx=4)

        # Текст стрелки
        text_frame = tk.Frame(parent, bg=Colors.SURFACE)
        text_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        tk.Label(
            text_frame,
            text="Текст на стрелке",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 5))

        # Поле ввода текста
        arrow_text_entry = tk.Entry(
            text_frame,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            highlightcolor=Colors.PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY
        )
        arrow_text_entry.pack(fill=tk.X, pady=(0, 0))
        self.fields["arrow_text"] = arrow_text_entry

        # Привязываем обработчик изменения
        arrow_text_entry.bind("<KeyRelease>", lambda e: self.on_arrow_text_changed())
        arrow_text_entry.bind("<FocusOut>", lambda e: self.on_arrow_text_changed())

        # Кнопка увеличения
        self.arrow_width_plus_btn = tk.Button(
            width_controls_frame,
            text="+",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            width=3,
            height=1,
            activebackground=Colors.ACTIVE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            command=lambda: self.change_arrow_width(1)
        )
        self.arrow_width_plus_btn.pack(side=tk.LEFT, padx=(8, 0))
        self.apply_hover_effect(self.arrow_width_plus_btn)
        
        # Стиль стрелки
        style_frame = tk.Frame(parent, bg=Colors.SURFACE)
        style_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        tk.Label(
            style_frame,
            text="Стиль линии",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Выпадающий список для стиля
        self.create_select_field(style_frame, "", "arrow_style", 
                               ["solid", "dashed", "dotted"])

    def create_card(self, parent, title):
        """Создает карточку с заголовком"""
        card_outer = tk.Frame(
            parent,
            bg=Colors.BACKGROUND,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        # Не упаковываем сразу - это будет сделано в update_properties
        # card_outer.pack(fill=tk.X, pady=(0, 16))

        card = tk.Frame(
            card_outer,
            bg=Colors.SURFACE
        )
        card.pack(fill=tk.X)

        # Заголовок карточки
        title_label = tk.Label(
            card,
            text=title,
            font=Fonts.SECTION,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(fill=tk.X, padx=14, pady=12)

        # Сохраняем ссылку на card_outer для управления видимостью
        card.card_outer = card_outer
        return card

    def create_field(self, parent, label_text, field_name, placeholder):
        """Создает поле ввода с меткой"""
        field_frame = tk.Frame(parent, bg=Colors.SURFACE)
        field_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        # Метка
        tk.Label(
            field_frame,
            text=label_text,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Поле ввода
        entry = tk.Entry(
            field_frame,
            font=Fonts.BODY,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            insertbackground=Colors.TEXT_PRIMARY
        )
        entry.insert(0, placeholder)
        entry.pack(fill=tk.X, pady=(5, 0))
        
        # Привязываем обработчик изменений
        entry.bind("<KeyRelease>", lambda e: self.on_field_changed(field_name, entry.get()))
        entry.bind("<FocusOut>", lambda e: self.on_field_changed(field_name, entry.get()))
        
        # Сохраняем ссылку на поле
        self.fields[field_name] = entry

    def create_select_field(self, parent, label_text, field_name, options):
        """Создает поле выбора с меткой"""
        field_frame = tk.Frame(parent, bg=Colors.SURFACE)
        field_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        # Метка
        tk.Label(
            field_frame,
            text=label_text,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Выпадающий список (имитация)
        combo_frame = tk.Frame(field_frame, bg=Colors.SURFACE, relief="flat", bd=0,
                               highlightthickness=1, highlightbackground=Colors.BORDER)
        combo_frame.pack(fill=tk.X, pady=(5, 0))

        entry = tk.Entry(
            combo_frame,
            font=Fonts.BODY,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground=Colors.TEXT_PRIMARY
        )
        if options:
            entry.insert(0, options[0])
        entry.pack(fill=tk.X, padx=8, pady=6)
        
        # Привязываем обработчик изменений
        entry.bind("<KeyRelease>", lambda e: self.on_field_changed(field_name, entry.get()))
        entry.bind("<FocusOut>", lambda e: self.on_field_changed(field_name, entry.get()))
        
        # Сохраняем ссылку на поле
        self.fields[field_name] = entry

    def create_small_field(self, parent, label_text, field_name, value, column):
        """Создает маленькое поле для сетки"""
        field_frame = tk.Frame(parent, bg=Colors.SURFACE)
        field_frame.grid(row=0, column=column, padx=(0, 10), sticky="ew")
        parent.columnconfigure(column, weight=1)

        # Метка
        tk.Label(
            field_frame,
            text=label_text,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        # Поле ввода
        entry = tk.Entry(
            field_frame,
            font=Fonts.BODY,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            insertbackground=Colors.TEXT_PRIMARY
        )
        entry.insert(0, value)
        entry.pack(fill=tk.X, padx=8, pady=(5, 0))
        
        # Привязываем обработчик изменений
        entry.bind("<KeyRelease>", lambda e: self.on_field_changed(field_name, entry.get()))
        entry.bind("<FocusOut>", lambda e: self.on_field_changed(field_name, entry.get()))
        
        # Сохраняем ссылку на поле
        self.fields[field_name] = entry

    def change_border_width(self, delta):
        """Изменение толщины границы"""
        new_width = self.current_border_width + delta
        # Ограничиваем диапазон от 1 до 10 пикселей
        if 1 <= new_width <= 10:
            self.current_border_width = new_width
            self.border_width_label.config(text=f"{new_width}px")
            
            # Отправляем изменение в блок
            if self.current_block and self.on_properties_change:
                update_data = {"border_width": new_width}
                self.on_properties_change(self.current_block, update_data)
    
    def change_arrow_width(self, delta):
        """Изменение толщины стрелки"""
        new_width = self.current_arrow_width + delta
        # Ограничиваем диапазон от 1 до 10 пикселей
        if 1 <= new_width <= 10:
            self.current_arrow_width = new_width
            self.arrow_width_label.config(text=f"{new_width}px")
            
            # Отправляем изменение в стрелку
            if self.current_block and isinstance(self.current_block, Arrow) and self.on_properties_change:
                update_data = {"width": new_width}
                self.on_properties_change(self.current_block, update_data)

    def on_field_changed(self, field_name, value):
        """Обработчик изменения значения в поле"""
        if self.current_block and self.on_properties_change:
            # Для числовых полей преобразуем значение
            if field_name in ["x", "y", "width", "height"]:
                try:
                    value = float(value)
                except ValueError:
                    return  # Неправильное числовое значение, игнорируем
            
            # Для стиля стрелки
            if field_name == "arrow_style":
                if isinstance(self.current_block, Arrow):
                    update_data = {"style": value}
                    self.on_properties_change(self.current_block, update_data)
                return
            
            # Обновляем данные в текущем блоке
            update_data = {field_name: value}
            self.on_properties_change(self.current_block, update_data)

    def on_color_selected(self, color):
        """Обработчик выбора цвета блока"""
        if self.current_block and isinstance(self.current_block, Block) and self.on_properties_change:
            update_data = {"color": color}
            self.on_properties_change(self.current_block, update_data)
            
            # ВАЖНО: Обновляем выделение цвета в панели
            current_color = color
            for swatch_color, swatch in self.color_swatches.items():
                if swatch_color == current_color:
                    swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
                else:
                    swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
    
    def on_arrow_text_changed(self):
        """Обработчик изменения текста стрелки"""
        if self.current_block and isinstance(self.current_block, Arrow) and self.on_properties_change:
            if "arrow_text" in self.fields:
                text = self.fields["arrow_text"].get()
                update_data = {"text": text}
                self.on_properties_change(self.current_block, update_data)
    
    def on_arrow_color_selected(self, color):
        """Обработчик выбора цвета стрелки"""
        if self.current_block and isinstance(self.current_block, Arrow) and self.on_properties_change:
            update_data = {"color": color}
            self.on_properties_change(self.current_block, update_data)
            
            # Обновляем выделение цвета в панели
            for swatch_color, swatch in self.arrow_color_swatches.items():
                if swatch_color == color:
                    swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
                else:
                    swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)

    def apply_hover_effect(self, widget, base_attr="SURFACE"):
        """Ховер-эффект с учетом текущей темы"""
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

    def update_properties(self, element):
        """Обновляет панель свойств для выбранного элемента (блока или стрелки)"""
        self.current_block = element
        
        # Скрываем/показываем карточки в зависимости от типа элемента
        if element is None:
            # Скрываем все карточки
            self.element_properties_card.card_outer.pack_forget()
            self.position_card.card_outer.pack_forget()
            self.style_card.card_outer.pack_forget()
            self.arrow_properties_card.card_outer.pack_forget()
            
            # Сбрасываем поля
            for field_name, entry in self.fields.items():
                entry.delete(0, tk.END)
                # Устанавливаем значения по умолчанию
                if field_name == "name":
                    entry.insert(0, "Введите название...")
                elif field_name == "code":
                    entry.insert(0, "A0")
                elif field_name == "element_type":
                    entry.insert(0, "Выберите тип")
                elif field_name == "description":
                    entry.insert(0, "Введите описание элемента...")
                elif field_name == "x":
                    entry.insert(0, "100")
                elif field_name == "y":
                    entry.insert(0, "150")
                elif field_name == "width":
                    entry.insert(0, "150")
                elif field_name == "height":
                    entry.insert(0, "80")
            
            # Сбрасываем толщину границы
            self.current_border_width = 2
            self.border_width_label.config(text="2px")
            
            # Сбрасываем выделение цветов
            for swatch in self.color_swatches.values():
                swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
            return
        
        # Определяем тип элемента
        if isinstance(element, Block):
            # Показываем карточки для блока
            self.element_properties_card.card_outer.pack(fill=tk.X, pady=(0, 16))
            self.position_card.card_outer.pack(fill=tk.X, pady=(0, 16))
            self.style_card.card_outer.pack(fill=tk.X, pady=(0, 16))
            self.arrow_properties_card.card_outer.pack_forget()
            
            # Обновляем поля значениями из блока
            block_data = element.to_dict()
            for field_name, entry in self.fields.items():
                if field_name in block_data:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(block_data[field_name]))
            
            # Обновляем толщину границы
            if "border_width" in block_data:
                self.current_border_width = block_data["border_width"]
                self.border_width_label.config(text=f"{self.current_border_width}px")
            
            # Подсвечиваем выбранный цвет
            current_color = block_data.get("color", "#E3F2FD")
            for color, swatch in self.color_swatches.items():
                if color == current_color:
                    swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
                else:
                    swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
        
        elif isinstance(element, Arrow):
            # Сохраняем ссылку на текущую стрелку
            self.current_block = element
            
            # Скрываем карточки для блоков
            self.element_properties_card.card_outer.pack_forget()
            self.position_card.card_outer.pack_forget()
            self.style_card.card_outer.pack_forget()
            
            # Показываем карточку для стрелки
            # Убеждаемся, что карточка видна
            self.arrow_properties_card.card_outer.pack(fill=tk.X, pady=(0, 16))
            
            # Обновляем свойства стрелки
            arrow_data = element.to_dict()
            
            # Обновляем толщину стрелки
            self.current_arrow_width = arrow_data.get("width", 2)
            if hasattr(self, 'arrow_width_label'):
                self.arrow_width_label.config(text=f"{self.current_arrow_width}px")
            
            # Обновляем текст стрелки
            if "arrow_text" in self.fields:
                arrow_text = arrow_data.get("text", "")
                self.fields["arrow_text"].delete(0, tk.END)
                self.fields["arrow_text"].insert(0, arrow_text)
            
            # Обновляем стиль стрелки
            if "arrow_style" in self.fields:
                self.fields["arrow_style"].delete(0, tk.END)
                self.fields["arrow_style"].insert(0, arrow_data.get("style", "solid"))
            
            # Подсвечиваем выбранный цвет стрелки
            current_color = arrow_data.get("color", "#E3F2FD")
            if hasattr(self, 'arrow_color_swatches'):
                for color, swatch in self.arrow_color_swatches.items():
                    if color == current_color:
                        swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
                    else:
                        swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
            
            print(f"Панель свойств стрелки обновлена: цвет={current_color}, ширина={self.current_arrow_width}, текст={arrow_data.get('text', '')}")
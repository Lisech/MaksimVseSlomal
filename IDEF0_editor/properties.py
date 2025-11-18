

import tkinter as tk
from styles import Colors, Dimensions, Fonts

class PropertiesPanel(tk.Frame):
    def __init__(self, parent, on_properties_change=None):
        super().__init__(parent, bg=Colors.BACKGROUND, width=Dimensions.PROPERTIES_WIDTH)
        self.pack_propagate(False)
        
        # Колбэк для уведомления об изменениях
        self.on_properties_change = on_properties_change
        
        # Текущий выбранный элемент
        self.current_element = None
        
        # Ссылки на виджеты для обновления
        self.fields = {}
        
        # Текущая толщина границы
        self.current_border_width = 2
        
        self.setup_ui()

    def setup_ui(self):
        # Основной контейнер
        content_frame = tk.Frame(self, bg=Colors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Сохраняем ссылку на content_frame для использования в обработчике
        self.content_frame = content_frame
        
        # Привязываем обработчик клика для потери фокуса полей ввода
        def remove_focus_from_entries():
            """Удаляет фокус со всех полей ввода, вызывая FocusOut"""
            focused_widget = self.focus_get()
            # Если фокус на поле ввода, вызываем событие FocusOut для сохранения изменений
            if focused_widget and isinstance(focused_widget, tk.Entry):
                # Создаем фиктивное событие для FocusOut, чтобы вызвать обработчик изменений
                focused_widget.event_generate("<FocusOut>")
            # Переводим фокус на панель
            self.focus_set()
        
        def on_panel_click(event):
            # Проверяем, не кликнули ли по полю ввода
            widget = event.widget
            if not isinstance(widget, tk.Entry):
                # Если клик не по полю ввода, удаляем фокус со всех полей
                # Используем after_idle, чтобы это произошло после обработки клика
                self.after_idle(remove_focus_from_entries)
        
        content_frame.bind("<Button-1>", on_panel_click)
        self.bind("<Button-1>", on_panel_click)

        # Карточка свойств элемента
        self.create_element_properties(content_frame)

        # Карточка позиции и размера
        self.create_position_card(content_frame)

        # Карточка стиля
        self.create_style_card(content_frame)
        
        # Карточка свойств стрелки (создается отдельно, но показывается только для стрелок)
        self.create_arrow_properties_card(content_frame)
        
        # Привязываем обработчик клика ко всем карточкам после их создания
        def bind_to_all_frames():
            """Привязывает обработчик клика ко всем фреймам для потери фокуса"""
            def bind_recursive(parent):
                """Рекурсивно привязывает обработчик ко всем фреймам"""
                for child in parent.winfo_children():
                    if isinstance(child, tk.Frame):
                        child.bind("<Button-1>", on_panel_click)
                        bind_recursive(child)
            
            for widget in content_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.bind("<Button-1>", on_panel_click)
                    bind_recursive(widget)
        
        self.after_idle(bind_to_all_frames)

    def create_element_properties(self, parent):
        """Карточка 'Свойства элемента'"""
        self.element_card = self.create_card(parent, "Свойства элемента")

        # Поле Название
        self.create_field(self.element_card, "Название", "name", "Введите название...")

        # Поле Код
        self.create_field(self.element_card, "Код", "code", "A0")

        # Поле Описание
        self.create_field(self.element_card, "Описание", "description", "Введите описание элемента...")

    def create_position_card(self, parent):
        """Карточка 'Позиция и размер'"""
        self.position_card = self.create_card(parent, "Позиция и размер")

        # Строка X, Y
        row1 = tk.Frame(self.position_card, bg=Colors.SURFACE)
        row1.pack(fill=tk.X, padx=14, pady=(0, 12))

        self.create_small_field(row1, "X", "x", "100", 0)
        self.create_small_field(row1, "Y", "y", "150", 1)

        # Строка Ширина, Высота
        row2 = tk.Frame(self.position_card, bg=Colors.SURFACE)
        row2.pack(fill=tk.X, padx=14)

        self.create_small_field(row2, "Ширина", "width", "150", 0)
        self.create_small_field(row2, "Высота", "height", "80", 1)

    def create_style_card(self, parent):
        """Карточка 'Стиль'"""
        self.style_card = self.create_card(parent, "Стиль")

        # Цвет заливки
        color_frame = tk.Frame(self.style_card, bg=Colors.SURFACE)
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
        border_frame = tk.Frame(self.style_card, bg=Colors.SURFACE)
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
        self.apply_hover_effect(self.border_minus_btn, base_bg=Colors.SURFACE, hover_bg=Colors.HOVER)

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
        self.apply_hover_effect(self.border_plus_btn, base_bg=Colors.SURFACE, hover_bg=Colors.HOVER)

    def create_arrow_properties_card(self, parent):
        """Карточка 'Свойства стрелки'"""
        self.arrow_card = self.create_card(parent, "Свойства стрелки")
        
        # Толщина стрелки
        arrow_width_frame = tk.Frame(self.arrow_card, bg=Colors.SURFACE)
        arrow_width_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        tk.Label(
            arrow_width_frame,
            text="Толщина стрелки",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        arrow_width_controls = tk.Frame(arrow_width_frame, bg=Colors.SURFACE)
        arrow_width_controls.pack(fill=tk.X, pady=(5, 0))

        self.arrow_width_minus_btn = tk.Button(
            arrow_width_controls,
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
        self.apply_hover_effect(self.arrow_width_minus_btn, base_bg=Colors.SURFACE, hover_bg=Colors.HOVER)

        self.arrow_width_label = tk.Label(
            arrow_width_controls,
            text="2px",
            font=("Segoe UI", 11),
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            width=6
        )
        self.arrow_width_label.pack(side=tk.LEFT, padx=4)

        self.arrow_width_plus_btn = tk.Button(
            arrow_width_controls,
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
        self.apply_hover_effect(self.arrow_width_plus_btn, base_bg=Colors.SURFACE, hover_bg=Colors.HOVER)

        # Стиль стрелки
        arrow_style_frame = tk.Frame(self.arrow_card, bg=Colors.SURFACE)
        arrow_style_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        tk.Label(
            arrow_style_frame,
            text="Стиль стрелки",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w")

        self.arrow_style_var = tk.StringVar(value="solid")
        arrow_style_controls = tk.Frame(arrow_style_frame, bg=Colors.SURFACE)
        arrow_style_controls.pack(fill=tk.X, pady=(5, 0))

        styles = [("Сплошная", "solid"), ("Пунктир", "dashed"), ("Точечная", "dotted")]
        for text, value in styles:
            rb = tk.Radiobutton(
                arrow_style_controls,
                text=text,
                variable=self.arrow_style_var,
                value=value,
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                selectcolor=Colors.SURFACE,
                activebackground=Colors.SURFACE,
                activeforeground=Colors.TEXT_PRIMARY,
                command=self.on_arrow_style_changed
            )
            rb.pack(side=tk.LEFT, padx=(0, 10))

    def create_card(self, parent, title):
        """Создает карточку с заголовком"""
        card_outer = tk.Frame(
            parent,
            bg=Colors.BACKGROUND,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        card_outer.pack(fill=tk.X, pady=(0, 16))

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
            if self.current_element and hasattr(self.current_element, 'border_width') and self.on_properties_change:
                update_data = {"border_width": new_width}
                self.on_properties_change(self.current_element, update_data)

    def change_arrow_width(self, delta):
        """Изменение толщины стрелки"""
        if self.current_element and hasattr(self.current_element, 'width'):
            new_width = self.current_element.width + delta
            # Ограничиваем диапазон от 1 до 10 пикселей
            if 1 <= new_width <= 10:
                self.arrow_width_label.config(text=f"{new_width}px")
                
                # Отправляем изменение в стрелку
                if self.on_properties_change:
                    update_data = {"width": new_width}
                    self.on_properties_change(self.current_element, update_data)

    def on_arrow_style_changed(self):
        """Обработчик изменения стиля стрелки"""
        if self.current_element and hasattr(self.current_element, 'style') and self.on_properties_change:
            update_data = {"style": self.arrow_style_var.get()}
            self.on_properties_change(self.current_element, update_data)

    def on_field_changed(self, field_name, value):
        """Обработчик изменения значения в поле"""
        if self.current_element and self.on_properties_change:
            # Для числовых полей преобразуем значение
            if field_name in ["x", "y", "width", "height"]:
                try:
                    value = float(value)
                except ValueError:
                    return  # Неправильное числовое значение, игнорируем
            
            # Обновляем данные в текущем элементе
            update_data = {field_name: value}
            self.on_properties_change(self.current_element, update_data)

    def on_color_selected(self, color):
        """Обработчик выбора цвета"""
        if self.current_element and self.on_properties_change:
            update_data = {"color": color}
            self.on_properties_change(self.current_element, update_data)
            
            # ВАЖНО: Обновляем выделение цвета в панели
            current_color = color
            for swatch_color, swatch in self.color_swatches.items():
                if swatch_color == current_color:
                    swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
                else:
                    swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)

    def apply_hover_effect(self, widget, base_bg=Colors.SURFACE, hover_bg=Colors.HOVER):
        """Базовый ховер-эффект - только смена цвета"""
        def on_enter(_):
            widget.configure(bg=hover_bg)
        def on_leave(_):
            widget.configure(bg=base_bg)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def update_properties(self, element):
        """Обновляет панель свойств для выбранного элемента"""
        self.current_element = element
        
        # Скрываем/показываем секции в зависимости от типа элемента
        if element is None:
            self.hide_all_sections()
            self.reset_all_fields()
            return
        
        from models import Block, Arrow
        
        if isinstance(element, Block):
            self.show_block_sections()
            self.update_block_properties(element)
        elif isinstance(element, Arrow):
            self.show_arrow_sections()
            self.update_arrow_properties(element)

    def hide_all_sections(self):
        """Скрывает все секции свойств"""
        self.element_card.pack_forget()
        self.position_card.pack_forget()
        self.style_card.pack_forget()
        self.arrow_card.pack_forget()

    def show_block_sections(self):
        """Показывает секции для блока"""
        self.element_card.pack(fill=tk.X, pady=(0, 16))
        self.position_card.pack(fill=tk.X, pady=(0, 16))
        self.style_card.pack(fill=tk.X, pady=(0, 16))
        self.arrow_card.pack_forget()

    def show_arrow_sections(self):
        """Показывает секции для стрелки"""
        # Получаем родительские контейнеры (card_outer) для управления позицией
        arrow_card_outer = self.arrow_card.master
        style_card_outer = self.style_card.master
        
        # Скрываем все карточки (работаем с card_outer, а не с внутренними card)
        self.element_card.master.pack_forget()
        self.position_card.master.pack_forget()
        style_card_outer.pack_forget()
        arrow_card_outer.pack_forget()
        
        # Показываем карточки в правильном порядке: сначала свойства стрелки, затем стиль
        # Первая карточка должна быть в самом верху с таким же отступом, как у блока
        # Упаковываем внешние контейнеры в правильном порядке, начиная с самого верха
        # Используем такой же формат, как для блока, чтобы отступы совпадали
        arrow_card_outer.pack(fill=tk.X, pady=(0, 16))
        style_card_outer.pack(fill=tk.X, pady=(0, 16))

    def reset_all_fields(self):
        """Сбрасывает все поля к значениям по умолчанию"""
        for field_name, entry in self.fields.items():
            entry.delete(0, tk.END)
            # Устанавливаем значения по умолчанию
            if field_name == "name":
                entry.insert(0, "Введите название...")
            elif field_name == "code":
                entry.insert(0, "A0")
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

    def update_block_properties(self, block):
        """Обновляет свойства для блока"""
        block_data = block.to_dict()
        for field_name, entry in self.fields.items():
            if field_name in block_data:
                entry.delete(0, tk.END)
                entry.insert(0, str(block_data[field_name]))
        
        # Обновляем толщину границы
        if "border_width" in block_data:
            self.current_border_width = block_data["border_width"]
            self.border_width_label.config(text=f"{self.current_border_width}px")
        
        # Подсвечиваем выбранный цвет
        current_color = block_data.get("color", Colors.BLOCK_FILL)
        for color, swatch in self.color_swatches.items():
            if color == current_color:
                swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
            else:
                swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)

    def update_arrow_properties(self, arrow):
        """Обновляет свойства для стрелки"""
        arrow_data = arrow.to_dict()
        
        # Обновляем толщину стрелки
        if "width" in arrow_data:
            self.arrow_width_label.config(text=f"{arrow_data['width']}px")
        
        # Обновляем стиль стрелки
        if "style" in arrow_data:
            self.arrow_style_var.set(arrow_data['style'])
        
        # Подсвечиваем выбранный цвет
        current_color = arrow_data.get("color", Colors.ARROW_COLOR)
        for color, swatch in self.color_swatches.items():
            if color == current_color:
                swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
            else:
                swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
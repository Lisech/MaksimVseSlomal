"""
Панель свойств - динамическое обновление свойств выбранного элемента
"""

import tkinter as tk
from styles import Colors, Dimensions, Fonts

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
        
        self.setup_ui()

    def setup_ui(self):
        # Основной контейнер
        content_frame = tk.Frame(self, bg=Colors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Карточка свойств элемента
        self.create_element_properties(content_frame)

        # Карточка позиции и размера
        self.create_position_card(content_frame)

        # Карточка стиля
        self.create_style_card(content_frame)

    def create_element_properties(self, parent):
        """Карточка 'Свойства элемента'"""
        card = self.create_card(parent, "Свойства элемента")

        # Поле Название
        self.create_field(card, "Название", "name", "Введите название...")

        # Поле Код
        self.create_field(card, "Код", "code", "A0")

        # Поле Тип элемента
        self.create_select_field(card, "Тип элемента", "element_type", 
                               ["Выберите тип", "Процесс", "Функция", "Действие", "Операция"])

        # Поле Описание
        self.create_field(card, "Описание", "description", "Введите описание элемента...")

    def create_position_card(self, parent):
        """Карточка 'Позиция и размер'"""
        card = self.create_card(parent, "Позиция и размер")

        # Строка X, Y
        row1 = tk.Frame(card, bg=Colors.SURFACE)
        row1.pack(fill=tk.X, padx=14, pady=(0, 12))

        self.create_small_field(row1, "X", "x", "100", 0)
        self.create_small_field(row1, "Y", "y", "150", 1)

        # Строка Ширина, Высота
        row2 = tk.Frame(card, bg=Colors.SURFACE)
        row2.pack(fill=tk.X, padx=14)

        self.create_small_field(row2, "Ширина", "width", "150", 0)
        self.create_small_field(row2, "Высота", "height", "80", 1)

    def create_style_card(self, parent):
        """Карточка 'Стиль'"""
        card = self.create_card(parent, "Стиль")

        # Цвет заливки
        color_frame = tk.Frame(card, bg=Colors.SURFACE)
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
        self.create_select_field(card, "Толщина границы", "border_width",
                               ["1px", "2px", "3px", "4px"])

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
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
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
            relief="flat",
            bd=0
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
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=Colors.BORDER
        )
        entry.insert(0, value)
        entry.pack(fill=tk.X, padx=8, pady=(5, 0))
        
        # Привязываем обработчик изменений
        entry.bind("<KeyRelease>", lambda e: self.on_field_changed(field_name, entry.get()))
        entry.bind("<FocusOut>", lambda e: self.on_field_changed(field_name, entry.get()))
        
        # Сохраняем ссылку на поле
        self.fields[field_name] = entry

    def on_field_changed(self, field_name, value):
        """Обработчик изменения значения в поле"""
        if self.current_block and self.on_properties_change:
            # Для числовых полей преобразуем значение
            if field_name in ["x", "y", "width", "height"]:
                try:
                    value = float(value)
                except ValueError:
                    return  # Неправильное числовое значение, игнорируем
            
            # Обновляем данные в текущем блоке
            update_data = {field_name: value}
            self.on_properties_change(self.current_block, update_data)

    def on_color_selected(self, color):
        """Обработчик выбора цвета"""
        if self.current_block and self.on_properties_change:
            update_data = {"color": color}
            self.on_properties_change(self.current_block, update_data)
            
            # ВАЖНО: Обновляем выделение цвета в панели
            current_color = color
            for swatch_color, swatch in self.color_swatches.items():
                if swatch_color == current_color:
                    swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
                else:
                    swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)

    def update_properties(self, block):
        """Обновляет панель свойств для выбранного блока"""
        self.current_block = block
        
        if block is None:
            # Сбрасываем поля если блок не выбран
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
            
            # Сбрасываем выделение цветов
            for swatch in self.color_swatches.values():
                swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
            return
        
        # Обновляем поля значениями из блока
        block_data = block.to_dict()
        for field_name, entry in self.fields.items():
            if field_name in block_data:
                entry.delete(0, tk.END)
                entry.insert(0, str(block_data[field_name]))
        
        # Подсвечиваем выбранный цвет - ВАЖНО: делаем это сразу
        current_color = block_data.get("color", "#E3F2FD")
        for color, swatch in self.color_swatches.items():
            if color == current_color:
                swatch.configure(highlightbackground=Colors.PRIMARY, highlightthickness=2)
            else:
                swatch.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
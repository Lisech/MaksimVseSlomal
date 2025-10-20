"""
Панель свойств - точная копия HTML макета
"""

import tkinter as tk
from styles import Colors, Dimensions, Fonts

class PropertiesPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BACKGROUND, width=Dimensions.PROPERTIES_WIDTH)
        self.pack_propagate(False)
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
        self.create_field(card, "Название", "Введите название...")

        # Поле Код
        self.create_field(card, "Код", "A0")

        # Поле Тип элемента
        self.create_select_field(card, "Тип элемента", ["Выберите тип"])

        # Поле Описание
        self.create_field(card, "Описание", "Введите описание элемента...")

    def create_position_card(self, parent):
        """Карточка 'Позиция и размер'"""
        card = self.create_card(parent, "Позиция и размер")

        # Строка X, Y
        row1 = tk.Frame(card, bg=Colors.BACKGROUND)
        row1.pack(fill=tk.X, padx=14, pady=(0, 12))

        self.create_small_field(row1, "X", "100", 0)
        self.create_small_field(row1, "Y", "150", 1)

        # Строка Ширина, Высота
        row2 = tk.Frame(card, bg=Colors.BACKGROUND)
        row2.pack(fill=tk.X, padx=14)

        self.create_small_field(row2, "Ширина", "120", 0)
        self.create_small_field(row2, "Высота", "80", 1)

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
            ("#ffffff", "white")
        ]

        for color, name in colors:
            swatch = tk.Frame(
                colors_frame,
                bg=color,
                width=30,
                height=24,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=Colors.BORDER
            )
            swatch.pack(side=tk.LEFT, padx=(0, 10), pady=2)
            swatch.pack_propagate(False)

        # Толщина границы
        self.create_select_field(card, "Толщина границы",
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

    def create_field(self, parent, label_text, placeholder):
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

    def create_select_field(self, parent, label_text, options):
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

    def create_small_field(self, parent, label_text, value, column):
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
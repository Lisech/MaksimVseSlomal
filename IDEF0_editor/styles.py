"""
Стили для IDEF0 Editor - точная копия HTML макета
"""

class Colors:
    # Палитры цветов для светлой и темной темы
    LIGHT = {
        "BACKGROUND": "#f6f7f9",
        "SURFACE": "#ffffff",
        "TEXT_PRIMARY": "#1f2328",
        "TEXT_SECONDARY": "#7a7f87",
        "PRIMARY": "#2d7ef7",
        "BORDER": "#edf1f5",
        "SIDEBAR": "#0f172a",
        "GRID": "#f0f0f0",
        "GRID_STRONG": "#e8e8e8",
        "ACTIVE": "#e8f0fe",
        "HOVER": "#f0f4f8",
        "BLOCK_FILL": "#E3F2FD",
        "BLOCK_BORDER": "#1f2328",
        "ARROW_COLOR": "#000000",  # Цвет стрелок по умолчанию (черный)
        "HANDLE_FILL": "#2d7ef7"  # Цвет маркеров и точек прикрепления (тот же PRIMARY для светлой темы)
    }
    
    DARK = {
        "BACKGROUND": "#0f172a",
        "SURFACE": "#1e293b",
        "TEXT_PRIMARY": "#f1f5f9",
        "TEXT_SECONDARY": "#94a3b8",
        "PRIMARY": "#3b82f6",
        "BORDER": "#334155",
        "SIDEBAR": "#0f172a",
        "GRID": "#1e293b",  # Темная сетка, видимая на темном фоне
        "GRID_STRONG": "#475569",  # Более светлая для основных линий (большие квадраты)
        "ACTIVE": "#1e3a5f",
        "HOVER": "#2d3748",
        "BLOCK_FILL": "#002137",
        "BLOCK_BORDER": "#94a3b8",
        "ARROW_COLOR": "#000000",  # Цвет стрелок по умолчанию для темной темы (черный)
        "HANDLE_FILL": "#002137"  # Цвет маркеров и точек прикрепления для темной темы
    }
    
    # Текущие цвета (по умолчанию светлая тема)
    BACKGROUND = LIGHT["BACKGROUND"]
    SURFACE = LIGHT["SURFACE"]
    TEXT_PRIMARY = LIGHT["TEXT_PRIMARY"]
    TEXT_SECONDARY = LIGHT["TEXT_SECONDARY"]
    PRIMARY = LIGHT["PRIMARY"]
    BORDER = LIGHT["BORDER"]
    SIDEBAR = LIGHT["SIDEBAR"]
    GRID = LIGHT["GRID"]
    GRID_STRONG = LIGHT["GRID_STRONG"]
    ACTIVE = LIGHT["ACTIVE"]
    HOVER = LIGHT["HOVER"]
    BLOCK_FILL = LIGHT["BLOCK_FILL"]
    BLOCK_BORDER = LIGHT["BLOCK_BORDER"]
    ARROW_COLOR = LIGHT["ARROW_COLOR"]
    HANDLE_FILL = LIGHT["HANDLE_FILL"]
    
    @classmethod
    def use_light(cls):
        """Переключает на светлую тему"""
        palette = cls.LIGHT
        cls.BACKGROUND = palette["BACKGROUND"]
        cls.SURFACE = palette["SURFACE"]
        cls.TEXT_PRIMARY = palette["TEXT_PRIMARY"]
        cls.TEXT_SECONDARY = palette["TEXT_SECONDARY"]
        cls.PRIMARY = palette["PRIMARY"]
        cls.BORDER = palette["BORDER"]
        cls.SIDEBAR = palette["SIDEBAR"]
        cls.GRID = palette["GRID"]
        cls.GRID_STRONG = palette["GRID_STRONG"]
        cls.ACTIVE = palette["ACTIVE"]
        cls.HOVER = palette["HOVER"]
        cls.BLOCK_FILL = palette["BLOCK_FILL"]
        cls.BLOCK_BORDER = palette["BLOCK_BORDER"]
        cls.ARROW_COLOR = palette["ARROW_COLOR"]
        cls.HANDLE_FILL = palette["HANDLE_FILL"]
    
    @classmethod
    def use_dark(cls):
        """Переключает на темную тему"""
        palette = cls.DARK
        cls.BACKGROUND = palette["BACKGROUND"]
        cls.SURFACE = palette["SURFACE"]
        cls.TEXT_PRIMARY = palette["TEXT_PRIMARY"]
        cls.TEXT_SECONDARY = palette["TEXT_SECONDARY"]
        cls.PRIMARY = palette["PRIMARY"]
        cls.BORDER = palette["BORDER"]
        cls.SIDEBAR = palette["SIDEBAR"]
        cls.GRID = palette["GRID"]
        cls.GRID_STRONG = palette["GRID_STRONG"]
        cls.ACTIVE = palette["ACTIVE"]
        cls.HOVER = palette["HOVER"]
        cls.BLOCK_FILL = palette["BLOCK_FILL"]
        cls.BLOCK_BORDER = palette["BLOCK_BORDER"]
        cls.ARROW_COLOR = palette["ARROW_COLOR"]
        cls.HANDLE_FILL = palette["HANDLE_FILL"]

class Dimensions:
    # Window
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700

    # Header
    HEADER_HEIGHT = 46

    # Layout
    LAYOUT_PADDING = 12
    SIDEBAR_WIDTH = 54
    PROPERTIES_WIDTH = 360
    
    # Grid
    GRID_MINOR_STEP = 20  # Шаг мелкой сетки в пикселях
    GRID_MAJOR_STEP = 100  # Шаг крупной сетки в пикселях

class Fonts:
    # Шрифты как в HTML макете
    TITLE = ("Segoe UI", 12, "bold")
    SECTION = ("Segoe UI", 11, "bold")
    BODY = ("Segoe UI", 10)
    SMALL = ("Segoe UI", 9)
    BUTTON = ("Segoe UI", 10)
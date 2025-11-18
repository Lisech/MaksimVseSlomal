"""
Стили и темы для IDEF0 Editor.

Добавлена поддержка светлой и тёмной темы с возможностью
переключения во время работы приложения.
"""


class Colors:
    """
    Глобальные цвета темы.

    Значения этих полей меняются методами `use_light` / `use_dark`,
    а остальной код просто использует `Colors.BACKGROUND` и т.п.
    """

    # Палитра светлой темы
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
        "HOVER": "#e2e8f0",
        "ACTIVE": "#e2e8f0",
        "BLOCK_FILL": "#E3F2FD",
        "BLOCK_BORDER": "#1f2328",
        "ARROW_COLOR": "#000000",
    }

    # Палитра тёмной темы (подобрана под стиль макета)
    DARK = {
        "BACKGROUND": "#020617",      # общий фон окна
        "SURFACE": "#020617",         # панели / хедер / холст
        "TEXT_PRIMARY": "#ffffff",
        "TEXT_SECONDARY": "#cbd5f5",
        "PRIMARY": "#3b82f6",
        "BORDER": "#1f2937",
        "SIDEBAR": "#020617",
        "GRID": "#111827",
        "GRID_STRONG": "#1f2937",
        "HOVER": "#1f2937",
        "ACTIVE": "#1f2937",
        "BLOCK_FILL": "#0f172a",
        "BLOCK_BORDER": "#ffffff",
        "ARROW_COLOR": "#ffffff",
    }

    # Текущие значения (будут переопределены при вызове use_light/use_dark)
    BACKGROUND = LIGHT["BACKGROUND"]
    SURFACE = LIGHT["SURFACE"]
    TEXT_PRIMARY = LIGHT["TEXT_PRIMARY"]
    TEXT_SECONDARY = LIGHT["TEXT_SECONDARY"]
    PRIMARY = LIGHT["PRIMARY"]
    BORDER = LIGHT["BORDER"]
    SIDEBAR = LIGHT["SIDEBAR"]
    GRID = LIGHT["GRID"]
    GRID_STRONG = LIGHT["GRID_STRONG"]
    HOVER = LIGHT["HOVER"]
    ACTIVE = LIGHT["ACTIVE"]
    BLOCK_FILL = LIGHT["BLOCK_FILL"]
    BLOCK_BORDER = LIGHT["BLOCK_BORDER"]
    ARROW_COLOR = LIGHT["ARROW_COLOR"]

    @classmethod
    def use_light(cls):
        """Переключить глобальные цвета на светлую тему."""
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
        cls.HOVER = palette["HOVER"]
        cls.ACTIVE = palette["ACTIVE"]
        cls.BLOCK_FILL = palette["BLOCK_FILL"]
        cls.BLOCK_BORDER = palette["BLOCK_BORDER"]
        cls.ARROW_COLOR = palette["ARROW_COLOR"]

    @classmethod
    def use_dark(cls):
        """Переключить глобальные цвета на тёмную тему."""
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
        cls.HOVER = palette["HOVER"]
        cls.ACTIVE = palette["ACTIVE"]
        cls.BLOCK_FILL = palette["BLOCK_FILL"]
        cls.BLOCK_BORDER = palette["BLOCK_BORDER"]
        cls.ARROW_COLOR = palette["ARROW_COLOR"]

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

class Fonts:
    # Шрифты как в HTML макете
    TITLE = ("Segoe UI", 12, "bold")
    SECTION = ("Segoe UI", 11, "bold")
    BODY = ("Segoe UI", 10)
    SMALL = ("Segoe UI", 9)
    BUTTON = ("Segoe UI", 10)
class Colors:
    # Светлая тема
    LIGHT = {
        "BACKGROUND": "#f6f7f9",
        "SURFACE": "#ffffff",
        "TEXT_PRIMARY": "#1f2328",
        "TEXT_SECONDARY": "#7a7f87",
        "PRIMARY": "#2d7ef7",
        "BORDER": "#edf1f5",
        "SIDEBAR": "#0f172a",
        "HOVER": "#e2e8f0",
        "ACTIVE": "#e2e8f0",
        "GRID": "#f0f0f0",
        "GRID_STRONG": "#e8e8e8",
        "BLOCK_FILL": "#E3F2FD",
        "BLOCK_BORDER": "#1f2328",
        "ARROW_COLOR": "#000000"
    }
    
    # Темная тема
    DARK = {
        "BACKGROUND": "#1a1d21",
        "SURFACE": "#2d3136",
        "TEXT_PRIMARY": "#ffffff",
        "TEXT_SECONDARY": "#8b949e",
        "PRIMARY": "#58a6ff",
        "BORDER": "#3d4248",
        "SIDEBAR": "#0d1117",
        "HOVER": "#3d4248",
        "ACTIVE": "#3d4248",
        "GRID": "#2d3136",
        "GRID_STRONG": "#3d4248",
        "BLOCK_FILL": "#1f2937",
        "BLOCK_BORDER": "#8b949e",
        "ARROW_COLOR": "#ffffff"
    }
    
    # Текущие цвета (по умолчанию светлая тема)
    BACKGROUND = LIGHT["BACKGROUND"]
    SURFACE = LIGHT["SURFACE"]
    TEXT_PRIMARY = LIGHT["TEXT_PRIMARY"]
    TEXT_SECONDARY = LIGHT["TEXT_SECONDARY"]
    PRIMARY = LIGHT["PRIMARY"]
    BORDER = LIGHT["BORDER"]
    SIDEBAR = LIGHT["SIDEBAR"]
    HOVER = LIGHT["HOVER"]
    ACTIVE = LIGHT["ACTIVE"]
    GRID = LIGHT["GRID"]
    GRID_STRONG = LIGHT["GRID_STRONG"]
    BLOCK_FILL = LIGHT["BLOCK_FILL"]
    BLOCK_BORDER = LIGHT["BLOCK_BORDER"]
    ARROW_COLOR = LIGHT["ARROW_COLOR"]
    
    @classmethod
    def use_light(cls):
        """Устанавливает светлую тему"""
        for key, value in cls.LIGHT.items():
            setattr(cls, key, value)
    
    @classmethod
    def use_dark(cls):
        """Устанавливает темную тему"""
        for key, value in cls.DARK.items():
            setattr(cls, key, value)


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
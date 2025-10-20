"""
Стили для IDEF0 Editor - точная копия HTML макета
"""

class Colors:
    # Основные цвета из HTML макета
    BACKGROUND = "#f6f7f9"
    SURFACE = "#ffffff"
    TEXT_PRIMARY = "#1f2328"
    TEXT_SECONDARY = "#7a7f87"
    PRIMARY = "#2d7ef7"
    BORDER = "#edf1f5"  # более тусклая светло‑серая граница
    SIDEBAR = "#0f172a"

    # Grid colors - заменяем RGBA на HEX
    GRID = "#f0f0f0"           # вместо rgba(0,0,0,0.04)
    GRID_STRONG = "#e8e8e8"    # вместо rgba(0,0,0,0.06)

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
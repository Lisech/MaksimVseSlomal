import os
import sys

# Добавляем путь к директории с модулями в sys.path
# Это нужно для правильной работы PyInstaller
if getattr(sys, 'frozen', False):
    # Если запущено из exe файла (onefile режим)
    # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        application_path = sys._MEIPASS
    else:
        # Если onedir режим
        application_path = os.path.dirname(sys.executable)
else:
    # Если запущено как скрипт
    application_path = os.path.dirname(os.path.abspath(__file__))

if application_path not in sys.path:
    sys.path.insert(0, application_path)

from app import IDEF0App

def main():
    print("Запуск IDEF0 Editor - Pixel Perfect макет")
    print("Все кнопки с заглушками")

    app = IDEF0App()
    app.run()

if __name__ == "__main__":
    main()
import os
import sys
import traceback


def main():
    try:
        # Определяем базовую директорию (работает и в frozen режиме, и в обычном)
        if getattr(sys, 'frozen', False):
            # Если запущено как exe (PyInstaller)
            base_dir = os.path.dirname(sys.executable)
        else:
            # Если запущено как скрипт
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Добавляем путь к текущей директории в sys.path для импортов
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        
        print("Запуск IDEF0 Editor - Pixel Perfect макет")
        print(f"Базовая директория: {base_dir}")
        
        # Импортируем модули
        from app import IDEF0App
        app = IDEF0App()
        app.run()
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print(f"\nТекущий sys.path: {sys.path}")
        print("\nУбедитесь, что все зависимости установлены:")
        print("pip install -r requirements.txt")
        print("\nУбедитесь, что вы запускаете из правильной директории:")
        print("cd IDEF0_editor")
        print("python main.py")
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
        sys.exit(1)


if __name__ == "__main__":
    main()
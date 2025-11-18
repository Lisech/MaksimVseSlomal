"""
Скрипт для пересборки IDEF0 Editor в exe файл
"""
import os
import sys
import subprocess
import shutil

def main():
    print("=" * 50)
    print("Пересборка IDEF0 Editor")
    print("=" * 50)
    print()
    
    # Получаем директорию скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Очистка старых файлов сборки
    print("Очистка старых файлов...")
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("  - Удалена папка build")
    
    if os.path.exists("dist/main.exe"):
        os.remove("dist/main.exe")
        print("  - Удален старый main.exe")
    
    print("Готово.")
    print()
    
    # Проверка наличия PyInstaller
    print("Проверка PyInstaller...")
    try:
        import PyInstaller
        print("  - PyInstaller найден")
    except ImportError:
        print("  - PyInstaller не найден. Устанавливаю...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("  - PyInstaller установлен")
        except subprocess.CalledProcessError:
            print("  - Ошибка установки PyInstaller!")
            return 1
    
    print()
    
    # Сборка exe
    print("Начинаю сборку exe...")
    print()
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "main.spec"])
        print()
        print("=" * 50)
        print("СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 50)
        print(f"Файл: {os.path.join('dist', 'main.exe')}")
        print()
        return 0
    except subprocess.CalledProcessError:
        print()
        print("=" * 50)
        print("ОШИБКА СБОРКИ!")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())


import os
import sys
import subprocess
import shutil
from pathlib import Path

# Добавляем путь к директории с модулями в sys.path
# Это нужно для правильной работы PyInstaller
if getattr(sys, 'frozen', False):
    # Если запущено из exe файла
    # Определяем путь к директории, где находится exe
    if hasattr(sys, '_MEIPASS'):
        # onefile режим - временная папка PyInstaller
        _meipass = sys._MEIPASS
        # Путь к директории с exe файлом
        exe_dir = os.path.dirname(sys.executable)
    else:
        # onedir режим
        exe_dir = os.path.dirname(sys.executable)
        _meipass = exe_dir
    
    application_path = exe_dir  # Путь к директории с exe
    source_path = exe_dir  # Ищем исходники рядом с exe
else:
    # Если запущено как скрипт
    application_path = os.path.dirname(os.path.abspath(__file__))
    source_path = application_path
    exe_dir = None
    _meipass = None

if application_path not in sys.path:
    sys.path.insert(0, application_path)


def find_python_executable():
    """Находит Python интерпретатор в системе"""
    # Пробуем разные варианты
    python_candidates = ['python', 'python3', 'py']
    
    for python_cmd in python_candidates:
        try:
            result = subprocess.run(
                [python_cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return python_cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    # Если ничего не найдено, пробуем использовать sys.executable
    # (но это может быть сам exe, поэтому это последний вариант)
    if not getattr(sys, 'frozen', False):
        return sys.executable
    
    # Для exe пытаемся найти python через PATH
    import shutil
    python_path = shutil.which('python')
    if python_path:
        return python_path
    
    return None


def rebuild_exe():
    """Быстрая пересборка exe файла при запуске"""
    print("=" * 50)
    print("Автоматическая пересборка exe...")
    print("=" * 50)
    
    # Определяем путь к исходникам
    if getattr(sys, 'frozen', False):
        # Если запущено из exe, ищем исходники рядом с exe
        source_dir = Path(exe_dir)
    else:
        # Если запущено как скрипт
        source_dir = Path(application_path)
    
    # Проверяем наличие исходных файлов
    main_py = source_dir / "main.py"
    app_py = source_dir / "app.py"
    
    if not main_py.exists() or not app_py.exists():
        print("Исходные файлы не найдены рядом с exe.")
        print(f"Ищем в: {source_dir}")
        print("Пропускаем пересборку.")
        return
    
    # Находим Python интерпретатор
    python_exe = find_python_executable()
    if not python_exe:
        print("Python интерпретатор не найден. Пропускаем пересборку.")
        return
    
    print(f"Используется Python: {python_exe}")
    
    # Проверяем наличие PyInstaller
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "show", "pyinstaller"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print("PyInstaller не найден. Устанавливаю...")
            subprocess.check_call([python_exe, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller установлен.")
    except Exception as e:
        print(f"Ошибка проверки PyInstaller: {e}")
        print("Пропускаем пересборку.")
        return
    
    # Очистка старых файлов сборки
    build_dir = source_dir / "build"
    if build_dir.exists():
        print("Очистка старых файлов сборки...")
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"Предупреждение: не удалось удалить build: {e}")
    
    # Удаляем старый exe (но не тот, который сейчас запущен)
    exe_path = source_dir / "dist" / "main.exe"
    current_exe = Path(sys.executable).resolve()
    
    if exe_path.exists():
        exe_path_resolved = exe_path.resolve()
        # Проверяем, что это не тот же файл, что запущен сейчас
        if exe_path_resolved != current_exe:
            print("Удаление старого exe...")
            try:
                exe_path.unlink()
            except Exception as e:
                print(f"Предупреждение: не удалось удалить старый exe: {e}")
        else:
            print("Пропускаем удаление - это текущий запущенный exe")
    
    # Создаем spec файл динамически
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img')],
    hiddenimports=['app', 'models', 'properties', 'styles'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Сохраняем временный spec файл
    spec_path = source_dir / "main_temp.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    try:
        # Запускаем PyInstaller
        print("Запуск PyInstaller...")
        result = subprocess.run(
            [python_exe, "-m", "PyInstaller", str(spec_path), "--clean", "--noconfirm"],
            cwd=source_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 минут максимум
        )
        
        if result.returncode == 0:
            print("=" * 50)
            print("ПЕРЕСБОРКА ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 50)
            print(f"Файл: {exe_path}")
        else:
            print("=" * 50)
            print("ОШИБКА ПЕРЕСБОРКИ!")
            print("=" * 50)
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
    except subprocess.TimeoutExpired:
        print("Превышено время ожидания пересборки.")
    except Exception as e:
        print(f"Ошибка при пересборке: {e}")
    finally:
        # Удаляем временный spec файл
        if spec_path.exists():
            try:
                spec_path.unlink()
            except:
                pass
    
    print()


def main():
    # Всегда выполняем пересборку (и для скрипта, и для exe)
    rebuild_exe()
    
    print("Запуск IDEF0 Editor - Pixel Perfect макет")
    print("Все кнопки с заглушками")

    from app import IDEF0App
    app = IDEF0App()
    app.run()


if __name__ == "__main__":
    main()
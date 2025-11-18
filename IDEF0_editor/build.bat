@echo off
echo ========================================
echo Пересборка IDEF0 Editor
echo ========================================
echo.

REM Очистка старых файлов сборки
echo Очистка старых файлов...
if exist build rmdir /s /q build
if exist dist\main.exe del /q dist\main.exe
echo Готово.
echo.

REM Проверка наличия PyInstaller
echo Проверка PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller не найден. Устанавливаю...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Ошибка установки PyInstaller!
        pause
        exit /b 1
    )
)
echo PyInstaller найден.
echo.

REM Сборка exe
echo Начинаю сборку exe...
pyinstaller main.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo ОШИБКА СБОРКИ!
    echo ========================================
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo СБОРКА ЗАВЕРШЕНА УСПЕШНО!
    echo ========================================
    echo Файл: dist\main.exe
    echo.
)

pause


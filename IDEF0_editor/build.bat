@echo off
echo Сборка IDEF0 Editor в exe файл...
echo.

REM Очистка предыдущих сборок
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Сборка exe файла...
pyinstaller main.spec

if %errorlevel% neq 0 (
    echo Ошибка при сборке!
    pause
    exit /b 1
)

echo.
echo Сборка завершена успешно!
echo exe файл находится в папке dist\
pause


@echo off
chcp 65001 >nul
echo Настройка Git конфигурации...
echo.

git config --global user.name "jawa350m1"
if errorlevel 1 (
    echo Ошибка настройки имени пользователя!
    pause
    exit /b 1
)
echo [OK] Имя пользователя установлено: jawa350m1

git config --global user.email "jawa350m1@gmail.com"
if errorlevel 1 (
    echo Ошибка настройки email!
    pause
    exit /b 1
)
echo [OK] Email установлен: jawa350m1@gmail.com

echo.
echo ====================================
echo Git конфигурация успешно настроена!
echo ====================================
echo.
echo Проверка настроек:
git config --global user.name
git config --global user.email
echo.
pause


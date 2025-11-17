@echo off
echo Добавление изменений...
git add .
if %errorlevel% neq 0 (
    echo Ошибка при добавлении файлов
    pause
    exit /b 1
)

echo Создание коммита...
git commit -m "реализация стрелок"
if %errorlevel% neq 0 (
    echo Ошибка при создании коммита (возможно, нет изменений)
    pause
    exit /b 1
)

echo Получение изменений с GitHub...
git pull origin master --no-rebase
if %errorlevel% neq 0 (
    echo Предупреждение: не удалось получить изменения с GitHub
)

echo Отправка изменений на GitHub...
git push origin master
if %errorlevel% neq 0 (
    echo Ошибка при отправке на GitHub
    pause
    exit /b 1
)

echo Успешно отправлено на GitHub!
pause


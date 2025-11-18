# Скрипт PowerShell для пересборки IDEF0 Editor
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Пересборка IDEF0 Editor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Очистка старых файлов сборки
Write-Host "Очистка старых файлов..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "  - Удалена папка build" -ForegroundColor Green
}

if (Test-Path "dist\main.exe") {
    Remove-Item -Force "dist\main.exe"
    Write-Host "  - Удален старый main.exe" -ForegroundColor Green
}

Write-Host "Готово." -ForegroundColor Green
Write-Host ""

# Проверка наличия PyInstaller
Write-Host "Проверка PyInstaller..." -ForegroundColor Yellow
$pyinstallerInstalled = python -m pip show pyinstaller 2>$null
if (-not $pyinstallerInstalled) {
    Write-Host "  - PyInstaller не найден. Устанавливаю..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  - Ошибка установки PyInstaller!" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    Write-Host "  - PyInstaller установлен" -ForegroundColor Green
} else {
    Write-Host "  - PyInstaller найден" -ForegroundColor Green
}

Write-Host ""

# Сборка exe
Write-Host "Начинаю сборку exe..." -ForegroundColor Yellow
Write-Host ""
pyinstaller main.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "СБОРКА ЗАВЕРШЕНА УСПЕШНО!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Файл: dist\main.exe" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ОШИБКА СБОРКИ!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Нажмите Enter для выхода"


Write-Host "Сборка IDEF0 Editor в exe файл..." -ForegroundColor Green
Write-Host ""

# Очистка предыдущих сборок
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

Write-Host "Установка зависимостей..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host ""
Write-Host "Сборка exe файла..." -ForegroundColor Green
pyinstaller main.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при сборке!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Сборка завершена успешно!" -ForegroundColor Green
Write-Host "exe файл находится в папке dist\" -ForegroundColor Green


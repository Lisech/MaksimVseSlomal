Write-Host "Добавление изменений..." -ForegroundColor Green
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при добавлении файлов" -ForegroundColor Red
    exit 1
}

Write-Host "Создание коммита..." -ForegroundColor Green
git commit -m "реализация стрелок"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при создании коммита (возможно, нет изменений)" -ForegroundColor Yellow
    exit 1
}

Write-Host "Получение изменений с GitHub..." -ForegroundColor Green
git pull origin master --no-rebase
if ($LASTEXITCODE -ne 0) {
    Write-Host "Предупреждение: не удалось получить изменения с GitHub" -ForegroundColor Yellow
}

Write-Host "Отправка изменений на GitHub..." -ForegroundColor Green
git push origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при отправке на GitHub" -ForegroundColor Red
    exit 1
}

Write-Host "Успешно отправлено на GitHub!" -ForegroundColor Green


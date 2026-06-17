@echo off
REM Скрипт запуска системы рекомендаций на Windows

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Система рекомендаций для интернет-магазина обоев      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python не установлен или не добавлен в PATH
    echo Пожалуйста, установите Python 3.8+ с https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python найден

REM Проверка зависимостей
echo.
echo Проверка зависимостей...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ✗ Зависимости не установлены
    echo Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ✗ Ошибка при установке зависимостей
        pause
        exit /b 1
    )
)

echo ✓ Зависимости установлены

REM Запуск сервера
echo.
echo ════════════════════════════════════════════════════════
echo Запуск API сервера...
echo ════════════════════════════════════════════════════════
echo.
echo API доступен по адресу: http://localhost:8000
echo Документация API: http://localhost:8000/docs
echo.
echo Нажмите Ctrl+C для остановки сервера
echo.

python main.py

pause

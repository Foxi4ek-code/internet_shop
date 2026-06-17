#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт запуска системы рекомендаций
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Проверка наличия необходимых пакетов"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'sklearn',
        'scipy'
    ]
    
    print("Проверка зависимостей...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nОтсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их командой: pip install -r requirements.txt")
        return False
    
    return True

def check_data_files():
    """Проверка наличия файлов данных"""
    current_dir = Path(__file__).parent
    products_path = current_dir / "products.json"
    
    print("\nПроверка файлов данных...")
    
    if not products_path.exists():
        print(f"✗ Файл {products_path} не найден")
        return False
    
    print(f"✓ {products_path}")
    return True

def start_api_server():
    """Запуск API сервера"""
    print("\n" + "="*50)
    print("Запуск системы рекомендаций...")
    print("="*50)
    print("\nAPI доступен по адресу: http://localhost:8000")
    print("Документация API: http://localhost:8000/docs")
    print("\nНажмите Ctrl+C для остановки сервера\n")
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\nСервер остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при запуске сервера: {e}")

def main():
    """Главная функция"""
    print("╔════════════════════════════════════════════════════╗")
    print("║  Система рекомендаций для интернет-магазина обоев  ║")
    print("╚════════════════════════════════════════════════════╝\n")
    
    # Проверка зависимостей
    if not check_dependencies():
        sys.exit(1)
    
    # Проверка файлов данных
    if not check_data_files():
        sys.exit(1)
    
    # Запуск сервера
    start_api_server()

if __name__ == "__main__":
    main()

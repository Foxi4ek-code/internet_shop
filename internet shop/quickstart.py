#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
БЫСТРЫЙ СТАРТ - Система рекомендаций

Этот скрипт настраивает и запускает полную систему рекомендаций
за несколько простых шагов.
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    """Печать приветственного заголовка"""
    header = """
╔════════════════════════════════════════════════════════════╗
║          СИСТЕМА РЕКОМЕНДАЦИЙ - БЫСТРЫЙ СТАРТ             ║
║          для интернет-магазина обоев                       ║
╚════════════════════════════════════════════════════════════╝

📚 Дипломный проект по системам рекомендаций товаров

"""
    print(header)

def check_python_version():
    """Проверка версии Python"""
    print("1️⃣  Проверка Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Требуется Python 3.8+, установлен Python {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} найден\n")
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("2️⃣  Установка зависимостей...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Файл {requirements_file} не найден")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✅ Зависимости установлены\n")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при установке зависимостей")
        return False

def check_data_files():
    """Проверка файлов данных"""
    print("3️⃣  Проверка файлов проекта...")
    
    required_files = [
        "products.json",
        "main.py",
        "recommenders.py",
        "data_preprocessor.py",
        "recommendations.js",
        "intmag.html"
    ]
    
    current_dir = Path(__file__).parent
    missing_files = []
    
    for file in required_files:
        file_path = current_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("✅ Все файлы найдены\n")
    return True

def print_usage_instructions():
    """Печать инструкций по использованию"""
    instructions = """
4️⃣  Готово к запуску!

📌 ИНСТРУКЦИИ:

Вариант 1 - Автоматический запуск (Windows):
  1. Откройте файл: run_server.bat
  2. API запустится на http://localhost:8000

Вариант 2 - Запуск из командной строки:
  Windows:
    > python main.py
  
  Linux/Mac:
    $ python3 main.py

Вариант 3 - Запуск скрипта (Windows):
  > python run_server.py

  Linux/Mac:
    $ python3 run_server.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 ПОСЛЕ ЗАПУСКА API:

1. Откройте браузер и перейдите на:
   📱 Сайт магазина:     http://localhost/intmag.html
   📚 Документация API:   http://localhost:8000/docs

2. Тестирование API (в отдельной консоли):
   > python examples.py

3. Оценка качества модели:
   > python evaluator.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 СТРУКТУРА ПРОЕКТА:

Backend:
  • main.py                  - FastAPI приложение
  • recommenders.py          - Алгоритмы рекомендаций
  • data_preprocessor.py     - Предобработка данных
  • evaluator.py             - Оценка качества
  
Frontend:
  • intmag.html              - HTML страница магазина
  • recommendations.js       - JavaScript клиент
  • styles.css              - Стили (обновлены)
  
Данные:
  • products.json            - Каталог товаров
  
Конфигурация:
  • config.json              - Параметры системы
  • requirements.txt         - Python зависимости

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 ОСНОВНЫЕ ВОЗМОЖНОСТИ:

✨ Персонализированные рекомендации
  Система учит предпочтения каждого пользователя и выдает 
  релевантные рекомендации товаров.

📊 Похожие товары
  Автоматическое предложение товаров, похожих на выбранный.

⭐ Популярные товары
  Показывает самые популярные товары в каталоге.

📈 Отслеживание взаимодействий
  Система записывает просмотры, клики и покупки для 
  улучшения рекомендаций.

🎯 Холодный старт
  Для новых пользователей автоматически предлагаются 
  популярные товары.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 API ЭНДПОИНТЫ:

POST /recommendations/personalized
  Получить персонализированные рекомендации

POST /recommendations/similar
  Получить похожие товары

GET /recommendations/popular
  Получить популярные товары

POST /interactions/track
  Отследить взаимодействие пользователя

GET /user/{user_id}/history
  Получить историю пользователя

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 НАСТРОЙКА:

Все параметры системы находятся в config.json:
  • Веса моделей (Item-CF: 60%, Content-based: 40%)
  • Количество соседей для Item-CF (по умолчанию 20)
  • Параметры кэширования
  • Настройки CORS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 СОВЕТЫ:

1. При первом запуске система генерирует синтетические данные
   для демонстрации. Это может занять несколько секунд.

2. Откройте http://localhost:8000/docs для интерактивной
   документации API и тестирования эндпоинтов.

3. В браузере откройте Console (F12) для просмотра логов.

4. Система автоматически отслеживает просмотры товаров.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ ПРОБЛЕМЫ?

• Ошибка подключения: убедитесь, что API запущен
• Медленная загрузка: попробуйте очистить кэш браузера
• CORS ошибки: проверьте, что frontend обращается к правильному URL
• Python ошибки: проверьте версию Python 3.8+

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 Больше информации в README.md

"""
    print(instructions)

def main():
    """Главная функция"""
    print_header()
    
    # Проверки
    if not check_python_version():
        return False
    
    if not check_data_files():
        return False
    
    if not install_dependencies():
        return False
    
    print_usage_instructions()
    
    # Вопрос о запуске
    response = input("Хотите запустить API сервер прямо сейчас? (y/n): ").strip().lower()
    
    if response in ['y', 'yes', 'да', 'д']:
        print("\n" + "="*60)
        print("🚀 Запуск API сервера...")
        print("="*60)
        print("\nAPI доступен по адресу: http://localhost:8000")
        print("Документация API: http://localhost:8000/docs")
        print("\nНажмите Ctrl+C для остановки сервера\n")
        
        try:
            subprocess.run([sys.executable, "main.py"])
        except KeyboardInterrupt:
            print("\n\n✅ Сервер остановлен")
    else:
        print("\n✅ Для запуска сервера выполните:")
        print("   python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

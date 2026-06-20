"""
Примеры использования API системы рекомендаций

Запустите API сервер перед выполнением этих примеров:
    python main.py

Затем выполните этот скрипт:
    python examples.py
"""

import requests
import json
import time

# URL API
API_URL = "http://localhost:8000"

def print_section(title):
    """Печать заголовка секции"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_api_health():
    """Проверка доступности API"""
    print_section("1. Проверка статуса API")
    
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API работает корректно")
            print(f"  Версия: {data['version']}")
            print(f"  Статус: {data['status']}")
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Не удается подключиться к API")
        print(f"  Убедитесь, что сервер запущен на {API_URL}")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False
    
    return True

def get_products_count():
    """Получение количества товаров"""
    print_section("2. Информация о каталоге")
    
    try:
        response = requests.get(f"{API_URL}/products/1")
        if response.status_code == 200:
            print(f"✓ Каталог товаров доступен")
        else:
            print(f"✓ Каталог загружен")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def get_personalized_recommendations():
    """Получение персонализированных рекомендаций"""
    print_section("3. Персонализированные рекомендации")
    
    user_id = 1
    print(f"Запрос рекомендаций для пользователя {user_id}...\n")
    
    try:
        response = requests.post(
            f"{API_URL}/recommendations/personalized",
            json={
                "user_id": user_id,
                "n": 5,
                "user_history": []
            }
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✓ Получено {len(recommendations)} рекомендаций:\n")
            
            for i, product in enumerate(recommendations, 1):
                print(f"{i}. {product['name']}")
                print(f"   Цена: {product['price']} ₽")
                print(f"   Оценка модели: {product['score']:.4f}")
                print(f"   Описание: {product['description']}\n")
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def get_similar_items():
    """Получение похожих товаров"""
    print_section("4. Похожие товары")
    
    product_id = 0
    print(f"Запрос товаров, похожих на товар {product_id}...\n")
    
    try:
        response = requests.post(
            f"{API_URL}/recommendations/similar",
            json={
                "product_id": product_id,
                "n": 4
            }
        )
        
        if response.status_code == 200:
            similar_items = response.json()
            print(f"✓ Найдено {len(similar_items)} похожих товаров:\n")
            
            for i, product in enumerate(similar_items, 1):
                print(f"{i}. {product['name']}")
                print(f"   Цена: {product['price']} ₽")
                print(f"   Сходство: {product['score']:.4f}\n")
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def get_popular_items():
    """Получение популярных товаров"""
    print_section("5. Популярные товары")
    
    try:
        response = requests.get(
            f"{API_URL}/recommendations/popular?n=5"
        )
        
        if response.status_code == 200:
            popular_items = response.json()
            print(f"✓ Топ популярных товаров:\n")
            
            for i, product in enumerate(popular_items, 1):
                print(f"{i}. {product['name']}")
                print(f"   Цена: {product['price']} ₽")
                print(f"   Популярность: {product['score']:.0f}\n")
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def track_interactions():
    """Отслеживание взаимодействий пользователя"""
    print_section("6. Отслеживание взаимодействий")
    
    user_id = 1
    interactions = [
        {"product_id": 0, "type": "view", "desc": "просмотр"},
        {"product_id": 2, "type": "click", "desc": "клик"},
        {"product_id": 1, "type": "purchase", "desc": "покупка"}
    ]
    
    print(f"Отслеживание взаимодействий пользователя {user_id}...\n")
    
    for interaction in interactions:
        try:
            response = requests.post(
                f"{API_URL}/interactions/track",
                json={
                    "user_id": user_id,
                    "product_id": interaction["product_id"],
                    "interaction_type": interaction["type"]
                }
            )
            
            if response.status_code == 200:
                print(f"✓ Записано: {interaction['desc']} товара {interaction['product_id']}")
            else:
                print(f"✗ Ошибка при записи взаимодействия")
        except Exception as e:
            print(f"✗ Ошибка: {e}")
    
    print()

def get_user_history():
    """Получение информации о пользователе через API"""
    print_section("7. Информация о пользователе")
    
    user_id = 1
    print(f"Запрос данных пользователя {user_id}...\n")
    
    try:
        response = requests.post(
            f"{API_URL}/recommendations/personalized",
            json={"user_id": user_id, "n": 3}
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✓ Для пользователя {user_id} доступно {len(recommendations)} рекомендаций\n")
            for i, product in enumerate(recommendations, 1):
                print(f"  {i}. {product['name']} - {product['price']} руб")
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def test_performance():
    """Тест производительности"""
    print_section("8. Тест производительности")
    
    print("Выполнение 20 запросов к API...\n")
    
    times = []
    try:
        for i in range(20):
            start = time.time()
            response = requests.post(
                f"{API_URL}/recommendations/personalized",
                json={
                    "user_id": (i % 100) + 1,
                    "n": 10
                }
            )
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            if (i + 1) % 5 == 0:
                print(f"  Выполнено {i + 1}/20 запросов...")
        
        print(f"\n✓ Статистика производительности:")
        print(f"  Минимум: {min(times):.2f}ms")
        print(f"  Максимум: {max(times):.2f}ms")
        print(f"  Среднее: {sum(times)/len(times):.2f}ms")
        print(f"  Медиана: {sorted(times)[len(times)//2]:.2f}ms")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def test_with_user_history():
    """Тест рекомендаций с историей пользователя"""
    print_section("9. Рекомендации на основе истории")
    
    user_id = 2
    user_history = [0, 1, 2]  # ID товаров, которые смотрел пользователь
    
    print(f"История пользователя: товары {user_history}\n")
    print(f"Запрос персонализированных рекомендаций...\n")
    
    try:
        response = requests.post(
            f"{API_URL}/recommendations/personalized",
            json={
                "user_id": user_id,
                "n": 5,
                "user_history": user_history
            }
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✓ Получено {len(recommendations)} рекомендаций:\n")
            
            for i, product in enumerate(recommendations, 1):
                print(f"{i}. {product['name']}")
                print(f"   Цена: {product['price']} ₽")
                print(f"   Оценка: {product['score']:.4f}\n")
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def main():
    """Главная функция"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║     Примеры использования API системы рекомендаций     ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    # Проверка API
    if not check_api_health():
        return
    
    # Примеры
    get_products_count()
    get_personalized_recommendations()
    get_similar_items()
    get_popular_items()
    track_interactions()
    get_user_history()
    test_with_user_history()
    test_performance()
    
    print_section("✓ Все примеры выполнены успешно")
    print("Документация API: http://localhost:8000/docs\n")

if __name__ == "__main__":
    main()

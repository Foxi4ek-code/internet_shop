import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
# Генерация синтетических данных для магазина "Дом Обоев"
np.random.seed(42)
# Генерация пользователей
n_users = 500
users = pd.DataFrame({
    'user_id': range(1, n_users + 1),
    'username': [f'user_{i}' for i in range(1, n_users + 1)],
    'registration_date': [
        datetime.now() - timedelta(days=random.randint(1, 730))
        for _ in range(n_users)
    ]
})
# Категории товаров магазина обоев
categories = pd.DataFrame({
    'category_id': range(1, 11),
    'name': [
        'Обои виниловые',
        'Обои флизелиновые', 
        'Фотообои',
        'Жидкие обои',
        'Ламинат',
        'Кварц-винил',
        'Керамогранит',
        'Клей обойный',
        'Клей монтажный',
        'Интерьерный декор'
    ]
})
# Бренды для каждой категории
brands_by_category = {
    1: ['Erismann', 'Rasch', 'AS Creation', 'Grandeco', 'Zambaiti'],  # Обои виниловые
    2: ['Marburg', 'Sirpi', 'Zambaiti', 'Decori&Decori', 'Эрисманн'],  # Обои флизелиновые
    3: ['Komar', 'Walltastic', 'Wellton', 'Affresco', '1Wall'],  # Фотообои
    4: ['Silk Plaster', 'Senideco', 'Cotex', 'Silkcoat', 'Bayramix'],  # Жидкие обои
    5: ['Kronostar', 'Tarkett', 'Quick-Step', 'Egger', 'Classen'],  # Ламинат
    6: ['Alpine Floor', 'Fine Floor', 'Art Tile', 'Vinilam', 'Aquafloor'],  # Кварц-винил
    7: ['Kerama Marazzi', 'Estima', 'Italon', 'Atlas Concorde', 'Cersanit'],  # Керамогранит
    8: ['Quelyd', 'Metylan', 'Kleo', 'PUFAS', 'Bostik'],  # Клей обойный
    9: ['Момент', 'Титан', 'Liquid Nails', 'Makroflex', 'Tytan'],  # Клей монтажный
    10: ['ИКЕА', 'Леруа Мерлен', 'Hoff', 'Mr.Doors', 'Стенли']  # Декор
}
# Генерация товаров
n_products = 300
products_list = []
for i in range(1, n_products + 1):
    category_id = random.randint(1, 10)
    brand = random.choice(brands_by_category[category_id])
    # Генерация цен в зависимости от категории
    price_ranges = {
        1: (500, 3500),    # Обои виниловые
        2: (600, 4000),    # Обои флизелиновые
        3: (1500, 8000),   # Фотообои
        4: (800, 2500),    # Жидкие обои
        5: (1200, 5000),   # Ламинат
        6: (1500, 6000),   # Кварц-винил
        7: (800, 4500),    # Керамогранит
        8: (200, 1500),    # Клей обойный
        9: (150, 1200),    # Клей монтажный
        10: (300, 5000)    # Декор
    }
    min_price, max_price = price_ranges[category_id]
    price = round(random.uniform(min_price, max_price), 2)
    # Генерация описаний
    category_name = categories[categories['category_id'] == category_id]['name'].values[0]
    description = f"{brand} {category_name} артикул {i:04d}. Высокое качество, долговечность."
    products_list.append({
        'product_id': i,
        'name': f'{brand} {category_name[:15]} #{i:04d}',
        'category_id': category_id,
        'brand': brand,
        'price': price,
        'description': description
    })
products = pd.DataFrame(products_list)
# Генерация взаимодействий (покупки, просмотры, клики)
n_interactions = 8000
interactions = []
for _ in range(n_interactions):
    user_id = random.randint(1, n_users)
    product_id = random.randint(1, n_products)
    interaction_type = random.choice(
        ['view', 'view', 'view', 'view', 'click', 'click', 'purchase']
    )
    interactions.append({
        'user_id': user_id,
        'product_id': product_id,
        'interaction_type': interaction_type,
        'timestamp': datetime.now() - timedelta(
            days=random.randint(1, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
    })
interactions_df = pd.DataFrame(interactions)
# Генерация оценок (ratings)
purchases = interactions_df[
    interactions_df['interaction_type'] == 'purchase'
]
ratings_data = []
for _, purchase in purchases.iterrows():
    # 70% покупок получают оценку
    if random.random() < 0.7:
        # Генерация оценок с уклоном в сторону высоких (реалистично)
        rating = random.choices(
            [1, 2, 3, 4, 5],
            weights=[0.05, 0.10, 0.15, 0.35, 0.35]
        )[0]
        ratings_data.append({
            'user_id': purchase['user_id'],
            'product_id': purchase['product_id'],
            'rating': rating,
            'timestamp': purchase['timestamp'] + timedelta(
                days=random.randint(1, 30)
            )
        })
ratings_df = pd.DataFrame(ratings_data)
# Сохранение данных в CSV
output_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(output_dir, exist_ok=True)
users.to_csv(os.path.join(output_dir, 'users.csv'), index=False, encoding='utf-8-sig')
categories.to_csv(os.path.join(output_dir, 'categories.csv'), index=False, encoding='utf-8-sig')
products.to_csv(os.path.join(output_dir, 'products.csv'), index=False, encoding='utf-8-sig')
interactions_df.to_csv(os.path.join(output_dir, 'interactions.csv'), index=False, encoding='utf-8-sig')
ratings_df.to_csv(os.path.join(output_dir, 'ratings.csv'), index=False, encoding='utf-8-sig')
print("=" * 60)
print("Синтетические данные успешно сгенерированы!")
print("=" * 60)
print(f"Пользователей: {len(users)}")
print(f"Категорий: {len(categories)}")
print(f"Товаров: {len(products)}")
print(f"Взаимодействий: {len(interactions_df)}")
print(f"  - Просмотров: {len(interactions_df[interactions_df['interaction_type'] == 'view'])}")
print(f"  - Кликов: {len(interactions_df[interactions_df['interaction_type'] == 'click'])}")
print(f"  - Покупок: {len(interactions_df[interactions_df['interaction_type'] == 'purchase'])}")
print(f"Оценок: {len(ratings_df)}")
print("=" * 60)
print("\nФайлы сохранены в папке: recommendation_system/data/")
print("  - users.csv")
print("  - categories.csv")
print("  - products.csv")
print("  - interactions.csv")
print("  - ratings.csv")
print("=" * 60)
# ---
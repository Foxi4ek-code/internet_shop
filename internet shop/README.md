# Интернет-магазин "Дом обоев" — система рекомендаций

Полнофункциональный интернет-магазин обоев с гибридной системой рекомендаций (ALS + Item-based CF + Content-based).

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

Дополнительно устанавливается библиотека `implicit` для ALS-рекомендаций.

### 2. Запуск сервера рекомендаций

```bash
python main.py
```

Сервер запустится на `http://localhost:8000`.

При первом запуске автоматически:
- загружаются товары из `products.json`
- генерируются синтетические взаимодействия пользователей
- обучаются модели (ALS, Item-based CF, Content-based)
- модель сохраняется в `models/hybrid_recommender.pkl` для быстрого старта в следующий раз

### 3. Открытие сайта

Открой файл `intmag.html` в любом браузере.

Сайт работает полностью на клиентской стороне (vanilla JS). Сервер рекомендаций нужен только для отображения блоков «Популярные обои» и «Рекомендовано для вас».

## Структура проекта

```
├── intmag.html              — Главная страница магазина
├── styles.css               — Все стили
├── products.json            — Каталог товаров (22 позиции)
├── recommendations.js       — Клиентская библиотека для API рекомендаций
├── main.py                  — FastAPI сервер рекомендаций
├── hybrid_recommender.py    — Гибридная модель (ALS + ItemCF + Content)
├── item_based_cf.py         — Коллаборативная фильтрация (Item-based CF)
├── als_recommender.py       — ALS матричная факторизация
├── content_based.py         — Контентная фильтрация
├── data_preprocessor.py     — Предобработка данных
├── generate_data.py         — Генерация синтетических данных
├── evaluate_models.py       — Оценка качества моделей
├── models/
│   └── hybrid_recommender.pkl — Сохранённая модель (создаётся автоматически)
├── products/                — Изображения товаров
├── logo.webp                — Логотип
├── mag.webp                 — Изображение магазина
└── Telegram_logo.svg.webp   — Иконка Telegram
```

## API эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/` | Статус API |
| POST | `/recommendations/personalized` | Персонализированные рекомендации |
| POST | `/recommendations/similar` | Похожие товары |
| GET | `/recommendations/popular?n=10&category_id=` | Популярные товары |
| POST | `/interactions/track` | Отслеживание действий пользователя |
| GET | `/categories` | Список категорий |
| GET | `/products/{product_id}` | Информация о товаре |

## Оценка качества

```bash
python evaluate_models.py
```

Результаты включают Precision@10, Recall@10, NDCG@10, Coverage, Novelty, Diversity и производительность.

## Особенности

- **Гибридная модель**: ALS (50%) + Item-based CF (30%) + Content-based (20%)
- **Кэширование**: in-memory кэш для быстрых повторных запросов
- **Персистентность**: модель сохраняется через pickle после первого обучения
- **Vanilla JS**: без фреймворков, всё на чистом HTML/CSS/JS
- **Корзина**: через localStorage
- **Toast-уведомления**: через Toastify

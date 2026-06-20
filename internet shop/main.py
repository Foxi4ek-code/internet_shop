from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pickle
import os
import pandas as pd
import json
from pathlib import Path
from data_preprocessor import DataPreprocessor
from item_based_cf import ItemBasedCF
from content_based import ContentBasedRecommender
from als_recommender import ALSRecommender
from hybrid_recommender import HybridRecommender
app = FastAPI(title="Recommendation System API - Дом Обоев")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
recommender = None
products_df = None
categories_df = None
interactions_df = None
class RecommendationRequest(BaseModel):
    user_id: int
    n: int = 10
class RecommendationResponse(BaseModel):
    product_id: int
    score: float
    name: str
    price: float
    category: str
    brand: str
    image: str = ""
    description: str = ""
class SimilarItemsRequest(BaseModel):
    product_id: int
    n: int = 10
class InteractionRequest(BaseModel):
    user_id: int
    product_id: int
    interaction_type: str
def get_product_info(product_id: int):
    if products_df is None:
        return None
    product = products_df[products_df['product_id'] == product_id]
    if product.empty:
        return None
    product = product.iloc[0]
    return {
        "product_id": int(product['product_id']),
        "name": product['name'],
        "price": float(product['price']),
        "category": product.get('category', product.get('material', 'Неизвестно')),
        "brand": product.get('brand', product.get('manufacturer', '')),
        "image": product.get('image', ''),
        "description": product.get('description', '')
    }
@app.on_event("startup")
def load_models():
    global recommender, products_df, categories_df, interactions_df
    base_dir = Path(__file__).parent
    models_dir = base_dir / "models"
    data_dir = base_dir / "data"
    model_path = models_dir / "hybrid_recommender.pkl"
    if model_path.exists():
        with open(model_path, 'rb') as f:
            recommender = pickle.load(f)
        print("Модель рекомендаций загружена")
    else:
        print("Модель не найдена. Выполняется обучение...")
        init_models()
        print("init_models завершён, данные products_df и interactions_df установлены")
        return
    products_path = data_dir / "products.csv"
    if products_path.exists():
        products_df = pd.read_csv(products_path)
        if 'product_id' not in products_df:
            products_df['product_id'] = range(len(products_df))
        print(f"Загружено {len(products_df)} товаров")
    else:
        json_path = base_dir / "products.json"
        if json_path.exists():
            products_df = pd.read_json(json_path)
            if 'product_id' not in products_df:
                products_df['product_id'] = range(len(products_df))
            print(f"Загружено {len(products_df)} товаров из JSON")
    categories_path = data_dir / "categories.csv"
    if categories_path.exists():
        categories_df = pd.read_csv(categories_path)
        print(f"Загружено {len(categories_df)} категорий")
    interactions_path = data_dir / "interactions.csv"
    if interactions_path.exists():
        interactions_df = pd.read_csv(interactions_path)
        print(f"Загружено {len(interactions_df)} взаимодействий")
    if interactions_df is None and products_df is not None:
        preprocessor = DataPreprocessor()
        preprocessor.products_df = products_df
        interactions_df = preprocessor.generate_synthetic_interactions(n_users=500, n_interactions=5000)
        print(f"Сгенерировано {len(interactions_df)} синтетических взаимодействий")
def init_models():
    global recommender, products_df, interactions_df
    base_dir = Path(__file__).parent
    products_path = base_dir / "products.json"
    if not products_path.exists():
        print("Файл products.json не найден")
        return
    preprocessor = DataPreprocessor()
    products_df = preprocessor.load_products_from_json(str(products_path))
    interactions_df = preprocessor.generate_synthetic_interactions(n_users=500, n_interactions=5000)
    preprocessor.create_user_item_matrix()
    product_features = preprocessor.extract_product_features()
    als = ALSRecommender(factors=50, regularization=0.01, iterations=15)
    item_cf = ItemBasedCF(k_neighbors=20)
    content_model = ContentBasedRecommender()
    als.fit(preprocessor.user_item_matrix)
    item_cf.fit(preprocessor.user_item_matrix)
    content_model.fit(product_features)
    recommender = HybridRecommender(als, item_cf, content_model)
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    with open(models_dir / "hybrid_recommender.pkl", 'wb') as f:
        pickle.dump(recommender, f)
    print("Модель обучена и сохранена")
@app.get("/")
def read_root():
    return {
        "message": "Recommendation System API - Дом Обоев",
        "version": "1.0",
        "status": "active" if recommender else "models_not_loaded"
    }
@app.post("/recommendations/personalized", response_model=List[RecommendationResponse])
def get_personalized_recommendations(request: RecommendationRequest):
    if recommender is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    try:
        user_history = []
        if interactions_df is not None:
            user_interactions = interactions_df[interactions_df['user_id'] == request.user_id]
            user_history = user_interactions['product_id'].tolist()
            user_history = [pid - 1 for pid in user_history if pid <= len(products_df)]
        recommendations = recommender.recommend(
            request.user_id - 1,
            user_history=user_history,
            n=request.n
        )
        result = []
        for product_id, score in recommendations:
            product_info = get_product_info(product_id + 1)
            if product_info:
                result.append({
                    "product_id": product_id + 1,
                    "score": float(score),
                    "name": product_info['name'],
                    "price": product_info['price'],
                    "category": product_info['category'],
                    "brand": product_info['brand'],
                    "image": product_info['image'],
                    "description": product_info['description']
                })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации рекомендаций: {str(e)}")
@app.post("/recommendations/similar", response_model=List[RecommendationResponse])
def get_similar_items(request: SimilarItemsRequest):
    if recommender is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    try:
        similar_items = recommender.get_similar_items(
            request.product_id - 1,
            n=request.n
        )
        result = []
        for product_id, score in similar_items:
            product_info = get_product_info(product_id + 1)
            if product_info:
                result.append({
                    "product_id": product_id + 1,
                    "score": float(score),
                    "name": product_info['name'],
                    "price": product_info['price'],
                    "category": product_info['category'],
                    "brand": product_info['brand'],
                    "image": product_info['image'],
                    "description": product_info['description']
                })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска похожих товаров: {str(e)}")
@app.get("/recommendations/popular", response_model=List[RecommendationResponse])
def get_popular_items(n: int = 10, category_id: Optional[int] = None):
    if products_df is None or interactions_df is None:
        raise HTTPException(status_code=503, detail="Данные не загружены")
    try:
        product_counts = interactions_df['product_id'].value_counts()
        if category_id:
            category_products = products_df[products_df['category_id'] == category_id]['product_id'].tolist()
            product_counts = product_counts[product_counts.index.isin(category_products)]
        top_products = product_counts.head(n)
        result = []
        for product_id, count in top_products.items():
            product_info = get_product_info(product_id)
            if product_info:
                result.append({
                    "product_id": product_id,
                    "score": float(count),
                    "name": product_info['name'],
                    "price": product_info['price'],
                    "category": product_info['category'],
                    "brand": product_info['brand'],
                    "image": product_info['image'],
                    "description": product_info['description']
                })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения популярных товаров: {str(e)}")
@app.post("/interactions/track")
def track_interaction(request: InteractionRequest):
    global interactions_df
    try:
        new_interaction = pd.DataFrame([{
            'user_id': request.user_id,
            'product_id': request.product_id,
            'interaction_type': request.interaction_type,
            'timestamp': pd.Timestamp.now()
        }])
        if interactions_df is not None:
            interactions_df = pd.concat([interactions_df, new_interaction], ignore_index=True)
        return {"status": "success", "message": "Взаимодействие сохранено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения взаимодействия: {str(e)}")
@app.get("/categories")
def get_categories():
    if products_df is None:
        raise HTTPException(status_code=503, detail="Товары не загружены")
    materials = products_df['material'].dropna().unique().tolist() if 'material' in products_df else []
    return [{"name": m} for m in materials]
@app.get("/products/{product_id}")
def get_product(product_id: int):
    product_info = get_product_info(product_id)
    if product_info is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product_info
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Запуск API сервера рекомендаций - Дом Обоев")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import pickle
import os
from pathlib import Path
import numpy as np
from datetime import datetime
from data_preprocessor import DataPreprocessor
from recommenders import ItemBasedCF, ContentBasedRecommender, ALSRecommender, HybridRecommender
app = FastAPI(
    title="Recommendation System API",
    description="API системы рекомендаций для интернет-магазина обоев",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class RecommendationRequest(BaseModel):
    user_id: int
    n: int = 10
    user_history: Optional[List[int]] = None
class SimilarItemsRequest(BaseModel):
    product_id: int
    n: int = 10
class RecommendationResponse(BaseModel):
    product_id: int
    score: float
    name: str
    price: float
    image: str
    description: str
class InteractionRequest(BaseModel):
    user_id: int
    product_id: int
    interaction_type: str
recommender = None
products_df = None
user_interactions_cache = {}
recommendations_cache = {}
MODEL_PATH = Path(__file__).parent / "models" / "hybrid_recommender.pkl"
def init_models():
    global recommender, products_df
    current_dir = Path(__file__).parent
    products_path = current_dir / "products.json"
    if not products_path.exists():
        raise FileNotFoundError(f"Файл {products_path} не найден")
    if MODEL_PATH.exists():
        try:
            with open(MODEL_PATH, 'rb') as f:
                saved = pickle.load(f)
                recommender = saved['recommender']
                products_df = saved['products_df']
            print("✓ Модели загружены из файла")
            return
        except Exception as e:
            print(f"Не удалось загрузить модели: {e}")
    preprocessor = DataPreprocessor()
    products_df = preprocessor.load_products_from_json(str(products_path))
    preprocessor.generate_synthetic_interactions(n_users=500, n_interactions=5000)
    preprocessor.create_user_item_matrix()
    als = ALSRecommender(factors=50, regularization=0.01, iterations=15)
    item_cf = ItemBasedCF(k_neighbors=20)
    content_model = ContentBasedRecommender()
    recommender = HybridRecommender(als, item_cf, content_model)
    recommender.fit(preprocessor.user_item_matrix, products_df)
    try:
        model_dir = MODEL_PATH.parent
        model_dir.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump({'recommender': recommender, 'products_df': products_df}, f)
        print("✓ Модели сохранены в файл")
    except Exception as e:
        print(f"Предупреждение: не удалось сохранить модели: {e}")
    print("✓ Модели инициализированы успешно")
@app.on_event("startup")
async def startup_event():
    try:
        init_models()
    except Exception as e:
        print(f"Ошибка при инициализации моделей: {e}")
@app.get("/")
def read_root():
    return {
        "message": "Recommendation System API",
        "version": "1.0",
        "status": "active"
    }
def _enrich_products(items):
    result = []
    for product_id, score in items:
        if product_id < len(products_df):
            product = products_df.iloc[product_id]
            result.append({
                "product_id": int(product_id),
                "score": float(score),
                "name": product.get('name', 'Unknown'),
                "price": float(product.get('price', 0)),
                "image": product.get('image', ''),
                "description": product.get('description', '')
            })
    return result
def _get_cache_key(prefix, *args):
    return f"{prefix}:{':'.join(str(a) for a in args)}"
@app.post("/recommendations/personalized", response_model=List[RecommendationResponse])
def get_personalized_recommendations(request: RecommendationRequest):
    try:
        if recommender is None:
            raise HTTPException(status_code=500, detail="Модели еще не инициализированы")
        cache_key = _get_cache_key('personalized', request.user_id, request.n)
        if cache_key in recommendations_cache:
            return recommendations_cache[cache_key]
        recommendations = recommender.recommend(
            user_id=request.user_id,
            user_history=request.user_history,
            n=request.n
        )
        result = _enrich_products(recommendations)
        recommendations_cache[cache_key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/recommendations/similar", response_model=List[RecommendationResponse])
def get_similar_items(request: SimilarItemsRequest):
    try:
        if recommender is None:
            raise HTTPException(status_code=500, detail="Модели еще не инициализированы")
        cache_key = _get_cache_key('similar', request.product_id, request.n)
        if cache_key in recommendations_cache:
            return recommendations_cache[cache_key]
        similar_items = recommender.get_similar_items(
            product_id=request.product_id,
            n=request.n
        )
        result = _enrich_products(similar_items)
        recommendations_cache[cache_key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/recommendations/popular")
def get_popular_items(n: int = 10, category_id: int = None):
    try:
        if recommender is None:
            raise HTTPException(status_code=500, detail="Модели еще не инициализированы")
        cache_key = _get_cache_key('popular', n, category_id)
        if cache_key in recommendations_cache:
            return recommendations_cache[cache_key]
        popular_items = recommender._get_popular_items(n)
        if category_id is not None:
            popular_items = [(pid, s) for pid, s in popular_items if pid < len(products_df) and products_df.iloc[pid].get('category_id') == category_id]
        result = _enrich_products(popular_items)
        recommendations_cache[cache_key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/interactions/track")
def track_interaction(request: InteractionRequest):
    try:
        key = f"user:{request.user_id}"
        if key not in user_interactions_cache:
            user_interactions_cache[key] = []
        user_interactions_cache[key].append({
            'product_id': request.product_id,
            'interaction_type': request.interaction_type,
            'timestamp': datetime.now().isoformat()
        })
        return {
            "status": "success",
            "message": "Взаимодействие успешно записано"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/user/{user_id}/history")
def get_user_history(user_id: int):
    try:
        key = f"user:{user_id}"
        history = user_interactions_cache.get(key, [])
        return {
            "user_id": user_id,
            "history": history,
            "total_interactions": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/products/count")
def get_products_count():
    try:
        return {
            "total_products": len(products_df) if products_df is not None else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
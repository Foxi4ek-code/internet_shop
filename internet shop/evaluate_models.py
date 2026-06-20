"""
Скрипт для оценки качества моделей рекомендаций
Вычисляет метрики: Precision@K, Recall@K, NDCG@K, Coverage
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle
from data_preprocessor import DataPreprocessor
class RecommenderEvaluator:
    """Оценка качества системы рекомендаций"""
    def __init__(self, test_data, model, user_item_matrix):
        self.test_data = test_data
        self.model = model
        self.user_item_matrix = user_item_matrix
    def calculate_mae(self):
        """Mean Absolute Error"""
        predictions = []
        actuals = []
        for _, row in self.test_data.iterrows():
            try:
                user_id = int(row['user_id']) - 1
                product_id = int(row['product_id']) - 1
                actual_rating = float(row['rating'])
                # Используем первый компонент гибридной модели
                try:
                    pred_rating = self.model.als_model.predict(user_id, product_id)
                except:
                    pred_rating = 0
                predictions.append(pred_rating)
                actuals.append(actual_rating)
            except:
                continue
        if len(predictions) == 0:
            return 0
        mae = mean_absolute_error(actuals, predictions)
        return mae
    def calculate_rmse(self):
        """Root Mean Squared Error"""
        predictions = []
        actuals = []
        for _, row in self.test_data.iterrows():
            try:
                user_id = int(row['user_id']) - 1
                product_id = int(row['product_id']) - 1
                actual_rating = float(row['rating'])
                try:
                    pred_rating = self.model.als_model.predict(user_id, product_id)
                except:
                    pred_rating = 0
                predictions.append(pred_rating)
                actuals.append(actual_rating)
            except:
                continue
        if len(predictions) == 0:
            return 0
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        return rmse
    def precision_at_k(self, k=10):
        """Precision@K"""
        precisions = []
        users = self.test_data['user_id'].unique()
        for user_id in users[:min(100, len(users))]:  # Ограничиваем для скорости
            try:
                user_id_int = int(user_id)
                relevant_items = set(
                    self.test_data[self.test_data['user_id'] == user_id]['product_id'].values
                )
                if len(relevant_items) == 0:
                    continue
                # Рекомендации модели
                recommendations = self.model.recommend(user_id_int - 1, n=k)
                recommended_ids = [pid + 1 for pid, _ in recommendations]
                # Пересечение
                hits = len(set(recommended_ids) & relevant_items)
                precision = hits / k if k > 0 else 0
                precisions.append(precision)
            except:
                continue
        return np.mean(precisions) if precisions else 0
    def recall_at_k(self, k=10):
        """Recall@K"""
        recalls = []
        users = self.test_data['user_id'].unique()
        for user_id in users[:min(100, len(users))]:
            try:
                user_id_int = int(user_id)
                relevant_items = set(
                    self.test_data[self.test_data['user_id'] == user_id]['product_id'].values
                )
                if len(relevant_items) == 0:
                    continue
                recommendations = self.model.recommend(user_id_int - 1, n=k)
                recommended_ids = [pid + 1 for pid, _ in recommendations]
                hits = len(set(recommended_ids) & relevant_items)
                recall = hits / len(relevant_items) if len(relevant_items) > 0 else 0
                recalls.append(recall)
            except:
                continue
        return np.mean(recalls) if recalls else 0
    def ndcg_at_k(self, k=10):
        """Normalized Discounted Cumulative Gain@K"""
        ndcgs = []
        users = self.test_data['user_id'].unique()
        for user_id in users[:min(100, len(users))]:
            try:
                user_id_int = int(user_id)
                user_test = self.test_data[self.test_data['user_id'] == user_id]
                if len(user_test) == 0:
                    continue
                # Релевантности из тестовой выборки
                relevance_dict = dict(zip(
                    user_test['product_id'].values,
                    user_test['rating'].values
                ))
                # Рекомендации
                recommendations = self.model.recommend(user_id_int - 1, n=k)
                # DCG
                dcg = 0
                for i, (pid, _) in enumerate(recommendations, 1):
                    rel = relevance_dict.get(pid + 1, 0)
                    dcg += (2**rel - 1) / np.log2(i + 1)
                # IDCG
                ideal_relevances = sorted(relevance_dict.values(), reverse=True)[:k]
                idcg = 0
                for i, rel in enumerate(ideal_relevances, 1):
                    idcg += (2**rel - 1) / np.log2(i + 1)
                if idcg > 0:
                    ndcg = dcg / idcg
                    ndcgs.append(ndcg)
            except:
                continue
        return np.mean(ndcgs) if ndcgs else 0
    def coverage(self, n_recommendations=10):
        """Покрытие каталога"""
        all_recommended = set()
        users = self.test_data['user_id'].unique()
        for user_id in users[:min(100, len(users))]:
            try:
                user_id_int = int(user_id)
                recommendations = self.model.recommend(user_id_int - 1, n=n_recommendations)
                all_recommended.update([pid + 1 for pid, _ in recommendations])
            except:
                continue
        total_items = self.user_item_matrix.shape[1]
        coverage = len(all_recommended) / total_items if total_items > 0 else 0
        return coverage
    def diversity(self, n_recommendations=10):
        """Разнообразие рекомендаций"""
        diversities = []
        users = self.test_data['user_id'].unique()
        for user_id in users[:min(50, len(users))]:
            try:
                user_id_int = int(user_id)
                recommendations = self.model.recommend(user_id_int - 1, n=n_recommendations)
                if len(recommendations) > 1:
                    # Вычисляем среднее расстояние между рекомендациями
                    products = [pid for pid, _ in recommendations]
                    diversity_score = len(set(products)) / len(products)
                    diversities.append(diversity_score)
            except:
                continue
        return np.mean(diversities) if diversities else 1.0
def main():
    print("=" * 60)
    print("ОЦЕНКА КАЧЕСТВА СИСТЕМЫ РЕКОМЕНДАЦИЙ")
    print("=" * 60)
    # Пути
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, 'data')
    models_dir = os.path.join(base_dir, 'models')
    # Загрузка данных
    print("\n[1/3] Загрузка данных...")
    try:
        interactions = pd.read_csv(os.path.join(data_dir, 'interactions.csv'))
        ratings = pd.read_csv(os.path.join(data_dir, 'ratings.csv'))
        products = pd.read_csv(os.path.join(data_dir, 'products.csv'))
        print(f"✓ Загружено {len(interactions)} взаимодействий")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return
    # Разделение на train/test
    print("\n[2/3] Подготовка данных...")
    preprocessor = DataPreprocessor()
    train_data, test_data = preprocessor.split_train_test(interactions, test_size=0.2)
    user_item_matrix, _ = preprocessor.create_user_item_matrix(train_data, ratings)
    # Загрузка модели
    print("\n[3/3] Загрузка модели...")
    model_path = os.path.join(models_dir, 'hybrid_recommender.pkl')
    if not os.path.exists(model_path):
        print(f"❌ Модель не найдена: {model_path}")
        print("Запустите train_models.py сначала")
        return
    with open(model_path, 'rb') as f:
        hybrid_model = pickle.load(f)
    print("✓ Модель загружена")
    # Оценка
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОЦЕНКИ")
    print("=" * 60)
    evaluator = RecommenderEvaluator(test_data, hybrid_model, user_item_matrix)
    print("\n📊 Метрики качества рекомендаций:")
    print("-" * 60)
    # Вычисляем метрики
    precision = evaluator.precision_at_k(k=10)
    recall = evaluator.recall_at_k(k=10)
    ndcg = evaluator.ndcg_at_k(k=10)
    coverage = evaluator.coverage(n_recommendations=10)
    diversity = evaluator.diversity(n_recommendations=10)
    mae = evaluator.calculate_mae()
    rmse = evaluator.calculate_rmse()
    print(f"Precision@10:  {precision:.4f}")
    print(f"Recall@10:     {recall:.4f}")
    print(f"NDCG@10:       {ndcg:.4f}")
    print(f"Coverage:      {coverage:.4f} ({coverage*100:.1f}%)")
    print(f"Diversity:     {diversity:.4f}")
    print(f"MAE:           {mae:.4f}")
    print(f"RMSE:          {rmse:.4f}")
    print("\n" + "=" * 60)
    print("ИНТЕРПРЕТАЦИЯ МЕТРИК")
    print("=" * 60)
    print("""
Precision@10  - Доля релевантных товаров в топ-10 рекомендациях
Recall@10     - Доля всех релевантных товаров, найденных в топ-10
NDCG@10       - Качество ранжирования рекомендаций (0-1)
Coverage      - Доля каталога, рекомендуемая системой (0-1)
Diversity     - Разнообразие рекомендаций (0-1)
MAE           - Средняя абсолютная ошибка предсказания оценок
RMSE          - Среднеквадратичная ошибка предсказания оценок
✓ Хорошие значения:
  - Precision > 0.15, Recall > 0.20
  - NDCG > 0.25
  - Coverage > 0.60
  - Diversity > 0.80
    """)
    # Сохранение результатов
    results = {
        'precision_at_10': float(precision),
        'recall_at_10': float(recall),
        'ndcg_at_10': float(ndcg),
        'coverage': float(coverage),
        'diversity': float(diversity),
        'mae': float(mae),
        'rmse': float(rmse)
    }
    results_path = os.path.join(models_dir, 'evaluation_results.txt')
    with open(results_path, 'w', encoding='utf-8') as f:
        for metric, value in results.items():
            f.write(f"{metric}: {value:.4f}\n")
    print(f"\n✓ Результаты сохранены: {results_path}")
    print("=" * 60 + "\n")
if __name__ == "__main__":
    main()
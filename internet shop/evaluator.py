import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, ndcg_score
import time
import random
class RecommenderEvaluator:
    def __init__(self, test_data):
        self.test_data = test_data
        self.metrics = {}
    def calculate_mae(self, model, user_item_matrix):
        predictions = []
        actuals = []
        for _, row in self.test_data.iterrows():
            try:
                user_id = int(row['user_id']) - 1
                product_id = int(row['product_id'])
                actual_rating = float(row.get('weight', row.get('rating', 1)))
                if user_id < 0 or user_id >= user_item_matrix.shape[0]:
                    continue
                if product_id < 0 or product_id >= user_item_matrix.shape[1]:
                    continue
                pred_rating = model.predict(user_id, product_id)
                predictions.append(pred_rating)
                actuals.append(actual_rating)
            except:
                continue
        if len(predictions) == 0:
            return 0.0
        mae = mean_absolute_error(actuals, predictions)
        return mae
    def calculate_rmse(self, model, user_item_matrix):
        predictions = []
        actuals = []
        for _, row in self.test_data.iterrows():
            try:
                user_id = int(row['user_id']) - 1
                product_id = int(row['product_id'])
                actual_rating = float(row.get('weight', row.get('rating', 1)))
                if user_id < 0 or user_id >= user_item_matrix.shape[0]:
                    continue
                if product_id < 0 or product_id >= user_item_matrix.shape[1]:
                    continue
                pred_rating = model.predict(user_id, product_id)
                predictions.append(pred_rating)
                actuals.append(actual_rating)
            except:
                continue
        if len(predictions) == 0:
            return 0.0
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        return rmse
    def precision_at_k(self, model, k=10):
        precisions = []
        users = self.test_data['user_id'].unique()
        for user_id in users:
            try:
                user_id_int = int(user_id)
                user_test = self.test_data[self.test_data['user_id'] == user_id]
                relevant_items = set(user_test['product_id'].values)
                if len(relevant_items) == 0:
                    continue
                recommendations = model.recommend(user_id_int - 1, n=k)
                if not recommendations:
                    precisions.append(0.0)
                    continue
                recommended_ids = [pid for pid, _ in recommendations]
                hits = len(set(recommended_ids) & relevant_items)
                precision = hits / k
                precisions.append(precision)
            except:
                continue
        return np.mean(precisions) if precisions else 0.0
    def recall_at_k(self, model, k=10):
        recalls = []
        users = self.test_data['user_id'].unique()
        for user_id in users:
            try:
                user_id_int = int(user_id)
                user_test = self.test_data[self.test_data['user_id'] == user_id]
                relevant_items = set(user_test['product_id'].values)
                if len(relevant_items) == 0:
                    continue
                recommendations = model.recommend(user_id_int - 1, n=k)
                if not recommendations:
                    recalls.append(0.0)
                    continue
                recommended_ids = [pid for pid, _ in recommendations]
                hits = len(set(recommended_ids) & relevant_items)
                recall = hits / len(relevant_items)
                recalls.append(recall)
            except:
                continue
        return np.mean(recalls) if recalls else 0.0
    def ndcg_at_k(self, model, k=10):
        ndcgs = []
        users = self.test_data['user_id'].unique()
        for user_id in users:
            try:
                user_id_int = int(user_id)
                user_test = self.test_data[self.test_data['user_id'] == user_id]
                if len(user_test) == 0:
                    continue
                relevance_dict = dict(zip(
                    user_test['product_id'].values,
                    user_test.get('weight', user_test.get('rating', [1] * len(user_test))).values
                ))
                recommendations = model.recommend(user_id_int - 1, n=k)
                if not recommendations:
                    continue
                dcg = 0
                for i, (pid, _) in enumerate(recommendations, 1):
                    rel = relevance_dict.get(pid, 0)
                    dcg += (2**rel - 1) / np.log2(i + 1)
                ideal_relevances = sorted(relevance_dict.values(), reverse=True)[:k]
                idcg = 0
                for i, rel in enumerate(ideal_relevances, 1):
                    idcg += (2**rel - 1) / np.log2(i + 1)
                if idcg > 0:
                    ndcgs.append(dcg / idcg)
            except:
                continue
        return np.mean(ndcgs) if ndcgs else 0.0
    def coverage(self, model, n_recommendations=10, n_users=100):
        all_recommended = set()
        for user_id in range(1, min(n_users + 1, 1000)):
            try:
                recommendations = model.recommend(user_id - 1, n=n_recommendations)
                all_recommended.update([pid for pid, _ in recommendations])
            except:
                continue
        total_items = model.user_item_matrix.shape[1]
        if total_items == 0:
            return 0.0
        coverage = min(len(all_recommended) / total_items, 1.0)
        return coverage
    def novelty(self, model, n_recommendations=10, n_users=100):
        item_popularity = np.array(model.user_item_matrix.sum(axis=0)).flatten()
        item_popularity = item_popularity / (item_popularity.max() + 1e-10)
        novelties = []
        for user_id in range(1, min(n_users + 1, 1000)):
            try:
                recommendations = model.recommend(user_id - 1, n=n_recommendations)
                if not recommendations:
                    continue
                rec_novelties = [1 - item_popularity[pid] for pid, _ in recommendations]
                novelties.extend(rec_novelties)
            except:
                continue
        return np.mean(novelties) if novelties else 0.0
    def diversity(self, model, n_recommendations=10, n_users=100):
        if not hasattr(model, 'item_cf_model') or not hasattr(model.item_cf_model, 'item_similarity_matrix'):
            return 0.0
        similarity_matrix = model.item_cf_model.item_similarity_matrix
        diversities = []
        for user_id in range(1, min(n_users + 1, 1000)):
            try:
                recommendations = model.recommend(user_id - 1, n=n_recommendations)
                if len(recommendations) < 2:
                    continue
                rec_ids = [pid for pid, _ in recommendations]
                similarities = []
                for i in range(len(rec_ids)):
                    for j in range(i + 1, len(rec_ids)):
                        sim = similarity_matrix[rec_ids[i], rec_ids[j]]
                        similarities.append(sim)
                if similarities:
                    avg_similarity = np.mean(similarities)
                    diversity = 1 - avg_similarity
                    diversities.append(diversity)
            except:
                continue
        return np.mean(diversities) if diversities else 0.0
    def measure_response_time(self, model, n_requests=50):
        times = []
        for _ in range(n_requests):
            user_id = random.randint(0, model.user_item_matrix.shape[0] - 1)
            start = time.time()
            recommendations = model.recommend(user_id, n=10)
            end = time.time()
            times.append((end - start) * 1000)
        return {
            'mean': np.mean(times),
            'median': np.median(times),
            'p95': np.percentile(times, 95),
            'p99': np.percentile(times, 99),
            'min': np.min(times),
            'max': np.max(times)
        }
    def evaluate_all(self, model, n_test_users=100):
        print("\n" + "="*60)
        print("ОЦЕНКА КАЧЕСТВА СИСТЕМЫ РЕКОМЕНДАЦИЙ")
        print("="*60)
        print("\n📊 Метрики качества рекомендаций:")
        print("-" * 60)
        precision = self.precision_at_k(model, k=10)
        recall = self.recall_at_k(model, k=10)
        ndcg = self.ndcg_at_k(model, k=10)
        coverage = self.coverage(model, n_users=n_test_users)
        novelty = self.novelty(model, n_users=n_test_users)
        diversity = self.diversity(model, n_users=n_test_users)
        print(f"Precision@10:  {precision:.4f}")
        print(f"Recall@10:     {recall:.4f}")
        print(f"NDCG@10:       {ndcg:.4f}")
        print(f"Coverage:      {coverage:.4f} ({coverage*100:.2f}%)")
        print(f"Novelty:       {novelty:.4f}")
        print(f"Diversity:     {diversity:.4f}")
        print("\n⚡ Производительность (миллисекунды):")
        print("-" * 60)
        perf = self.measure_response_time(model, n_requests=50)
        print(f"Mean:          {perf['mean']:.2f}ms")
        print(f"Median:        {perf['median']:.2f}ms")
        print(f"P95:           {perf['p95']:.2f}ms")
        print(f"P99:           {perf['p99']:.2f}ms")
        print(f"Min:           {perf['min']:.2f}ms")
        print(f"Max:           {perf['max']:.2f}ms")
        self.metrics = {
            'precision@10': precision,
            'recall@10': recall,
            'ndcg@10': ndcg,
            'coverage': coverage,
            'novelty': novelty,
            'diversity': diversity,
            'response_time': perf
        }
        print("\n" + "="*60)
        return self.metrics
    def generate_report(self, model, model_name="Hybrid Model", n_test_users=100):
        metrics = self.evaluate_all(model, n_test_users)
        report = f
        if metrics['precision@10'] > 0.2:
            report += "✓ Хороший уровень точности рекомендаций\n"
        if metrics['coverage'] > 0.7:
            report += "✓ Хорошее покрытие каталога товаров\n"
        if metrics['response_time']['p95'] < 200:
            report += "✓ Приемлемое время отклика API\n"
        if metrics['diversity'] > 0.6:
            report += "✓ Хорошее разнообразие рекомендаций\n"
        report += f
        return report
def run_evaluation_demo():
    from data_preprocessor import DataPreprocessor
    from recommenders import ItemBasedCF, ContentBasedRecommender, ALSRecommender, HybridRecommender
    from pathlib import Path
    print("Загрузка данных...")
    preprocessor = DataPreprocessor()
    current_dir = Path(__file__).parent
    products_path = current_dir / "products.json"
    products_df = preprocessor.load_products_from_json(str(products_path))
    preprocessor.generate_synthetic_interactions(n_users=500, n_interactions=5000)
    preprocessor.create_user_item_matrix()
    train, test = preprocessor.split_train_test(test_size=0.2)
    print("Обучение моделей...")
    als = ALSRecommender(factors=50, regularization=0.01, iterations=15)
    item_cf = ItemBasedCF(k_neighbors=20)
    content_model = ContentBasedRecommender()
    recommender = HybridRecommender(als, item_cf, content_model)
    recommender.fit(preprocessor.user_item_matrix, products_df)
    print("Оценка качества...")
    evaluator = RecommenderEvaluator(test)
    report = evaluator.generate_report(recommender, "Гибридная модель (ALS + ItemCF + Content)", n_test_users=100)
    print(report)
    return evaluator.metrics
if __name__ == "__main__":
    metrics = run_evaluation_demo()
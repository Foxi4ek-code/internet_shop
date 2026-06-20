import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
class ItemBasedCF:
    """Item-based Collaborative Filtering"""
    def __init__(self, k_neighbors=20):
        self.k_neighbors = k_neighbors
        self.item_similarity_matrix = None
        self.user_item_matrix = None
    def fit(self, user_item_matrix):
        """
        Обучение модели - вычисление схожести между товарами
        Args:
            user_item_matrix: разреженная матрица пользователь-товар
        """
        self.user_item_matrix = user_item_matrix
        # Вычисление косинусного сходства между товарами
        # Транспонируем, чтобы строки были товарами
        item_matrix = user_item_matrix.T
        self.item_similarity_matrix = cosine_similarity(item_matrix)
        # Обнуляем диагональ (схожесть товара с самим собой)
        np.fill_diagonal(self.item_similarity_matrix, 0)
        print(f"Item-based CF: матрица схожести {self.item_similarity_matrix.shape}")
    def get_similar_items(self, product_id, n=10):
        """
        Получение похожих товаров
        Args:
            product_id: ID товара (начиная с 0)
            n: количество похожих товаров
        Returns:
            list: список кортежей (product_id, similarity_score)
        """
        if product_id >= self.item_similarity_matrix.shape[0]:
            return []
        similarities = self.item_similarity_matrix[product_id]
        # Топ-N похожих товаров
        similar_indices = np.argsort(similarities)[::-1][:n]
        similar_scores = similarities[similar_indices]
        return list(zip(similar_indices, similar_scores))
    def predict(self, user_id, product_id):
        """
        Предсказание оценки пользователя для товара
        Args:
            user_id: ID пользователя (начиная с 0)
            product_id: ID товара (начиная с 0)
        Returns:
            float: предсказанная оценка
        """
        if user_id >= self.user_item_matrix.shape[0]:
            return 0
        # Товары, которые оценил пользователь
        user_ratings = self.user_item_matrix[user_id].toarray().flatten()
        rated_indices = np.where(user_ratings > 0)[0]
        if len(rated_indices) == 0:
            return 0
        # Схожести целевого товара с оцененными
        similarities = self.item_similarity_matrix[product_id, rated_indices]
        # Топ-K наиболее похожих
        top_k_idx = np.argsort(similarities)[::-1][:self.k_neighbors]
        top_similarities = similarities[top_k_idx]
        top_ratings = user_ratings[rated_indices[top_k_idx]]
        # Взвешенное среднее
        if np.sum(np.abs(top_similarities)) == 0:
            return 0
        prediction = np.sum(top_similarities * top_ratings) / np.sum(np.abs(top_similarities))
        return prediction
    def recommend(self, user_id, n=10, exclude_rated=True):
        """
        Рекомендации для пользователя
        Args:
            user_id: ID пользователя (начиная с 0)
            n: количество рекомендаций
            exclude_rated: исключить уже оцененные товары
        Returns:
            list: список кортежей (product_id, predicted_score)
        """
        if user_id >= self.user_item_matrix.shape[0]:
            return []
        user_ratings = self.user_item_matrix[user_id].toarray().flatten()
        rated_indices = np.where(user_ratings > 0)[0]
        # Предсказываем оценки для всех товаров
        n_items = self.user_item_matrix.shape[1]
        predictions = []
        for product_id in range(n_items):
            if exclude_rated and product_id in rated_indices:
                continue
            score = self.predict(user_id, product_id)
            predictions.append((product_id, score))
        # Сортируем по убыванию оценки
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]
# ---
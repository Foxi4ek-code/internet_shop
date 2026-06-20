import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
class ContentBasedRecommender:
    """Content-based фильтрация на основе признаков товаров"""
    def __init__(self):
        self.product_features = None
        self.similarity_matrix = None
    def fit(self, product_features):
        """
        Обучение на признаках товаров
        Args:
            product_features: матрица признаков товаров
        """
        self.product_features = product_features
        # Вычисление матрицы схожести
        self.similarity_matrix = cosine_similarity(product_features)
        np.fill_diagonal(self.similarity_matrix, 0)
        print(f"Content-based: матрица схожести {self.similarity_matrix.shape}")
    def get_similar_items(self, product_id, n=10):
        """
        Похожие товары по контенту
        Args:
            product_id: ID товара (начиная с 0)
            n: количество похожих товаров
        Returns:
            list: список кортежей (product_id, similarity_score)
        """
        if product_id >= self.similarity_matrix.shape[0]:
            return []
        similarities = self.similarity_matrix[product_id]
        similar_indices = np.argsort(similarities)[::-1][:n]
        similar_scores = similarities[similar_indices]
        return list(zip(similar_indices, similar_scores))
    def recommend_for_user(self, user_history, n=10):
        """
        Рекомендации на основе истории пользователя
        Args:
            user_history: список ID товаров из истории пользователя
            n: количество рекомендаций
        Returns:
            list: список кортежей (product_id, similarity_score)
        """
        if len(user_history) == 0:
            return []
        # Фильтруем историю, чтобы индексы были в пределах матрицы
        valid_history = [pid for pid in user_history if pid < self.product_features.shape[0]]
        if len(valid_history) == 0:
            return []
        # Усредняем признаки товаров из истории пользователя
        user_profile = np.mean(
            self.product_features[valid_history].toarray(),
            axis=0
        )
        # Вычисляем схожесть со всеми товарами
        similarities = cosine_similarity(
            user_profile.reshape(1, -1),
            self.product_features
        ).flatten()
        # Исключаем товары из истории
        similarities[valid_history] = 0
        # Топ-N рекомендаций
        top_indices = np.argsort(similarities)[::-1][:n]
        top_scores = similarities[top_indices]
        return list(zip(top_indices, top_scores))
    def predict(self, user_id, product_id):
        """
        Заглушка для совместимости с другими моделями
        Args:
            user_id: ID пользователя
            product_id: ID товара
        Returns:
            float: 0 (не используется в content-based)
        """
        return 0.0
import numpy as np
from implicit.als import AlternatingLeastSquares
class ALSRecommender:
    """Matrix Factorization using Alternating Least Squares"""
    def __init__(self, factors=50, regularization=0.01, iterations=15):
        """
        Инициализация модели ALS
        Args:
            factors: количество латентных факторов
            regularization: параметр регуляризации
            iterations: количество итераций обучения
        """
        self.model = AlternatingLeastSquares(
            factors=factors,
            regularization=regularization,
            iterations=iterations,
            use_gpu=False
        )
        self.user_item_matrix = None
    def fit(self, user_item_matrix):
        """
        Обучение модели ALS
        Args:
            user_item_matrix: разреженная матрица пользователь-товар
        """
        self.user_item_matrix = user_item_matrix
        # implicit требует формат item-user
        item_user_matrix = user_item_matrix.T.tocsr()
        self.model.fit(item_user_matrix)
        print(f"ALS модель обучена с {self.model.factors} факторами")
    def recommend(self, user_id, n=10, filter_already_liked=True):
        """
        Рекомендации для пользователя
        Args:
            user_id: ID пользователя (начиная с 0)
            n: количество рекомендаций
            filter_already_liked: исключить уже понравившиеся товары
        Returns:
            list: список кортежей (product_id, score)
        """
        try:
            recommendations = self.model.recommend(
                user_id,
                self.user_item_matrix[user_id],
                N=n,
                filter_already_liked_items=filter_already_liked
            )
            # Возвращаем (product_id, score)
            return [(item_id, score) for item_id, score in zip(recommendations[0], recommendations[1])]
        except Exception as e:
            print(f"Ошибка рекомендаций ALS для пользователя {user_id}: {e}")
            return []
    def similar_items(self, product_id, n=10):
        """
        Похожие товары
        Args:
            product_id: ID товара (начиная с 0)
            n: количество похожих товаров
        Returns:
            list: список кортежей (item_id, score)
        """
        try:
            similar = self.model.similar_items(product_id, N=n)
            return [(item_id, score) for item_id, score in zip(similar[0], similar[1])]
        except Exception as e:
            print(f"Ошибка поиска похожих товаров для {product_id}: {e}")
            return []
    def predict(self, user_id, product_id):
        """
        Предсказание оценки пользователя для товара (для совместимости)
        Args:
            user_id: ID пользователя (начиная с 0)
            product_id: ID товара (начиная с 0)
        Returns:
            float: предсказанная оценка
        """
        try:
            # Получаем латентные векторы
            user_vector = self.model.user_factors[user_id]
            item_vector = self.model.item_factors[product_id]
            # Скалярное произведение
            score = np.dot(user_vector, item_vector)
            return float(score)
        except Exception as e:
            return 0.0
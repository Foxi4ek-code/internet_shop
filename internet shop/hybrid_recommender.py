import numpy as np
class HybridRecommender:
    """Гибридная модель рекомендаций, объединяющая ALS, Item-CF и Content-based"""
    def __init__(self, als_model, item_cf_model, content_model):
        """
        Инициализация гибридной модели
        Args:
            als_model: модель ALS
            item_cf_model: модель Item-based CF
            content_model: модель Content-based
        """
        self.als_model = als_model
        self.item_cf_model = item_cf_model
        self.content_model = content_model
        # Веса для комбинирования
        self.weights = {
            'als': 0.5,
            'item_cf': 0.3,
            'content': 0.2
        }
    def set_weights(self, als_weight, cf_weight, content_weight):
        """
        Установка весов моделей
        Args:
            als_weight: вес для ALS
            cf_weight: вес для Item-CF
            content_weight: вес для Content-based
        """
        total = als_weight + cf_weight + content_weight
        self.weights = {
            'als': als_weight / total,
            'item_cf': cf_weight / total,
            'content': content_weight / total
        }
        print(f"Веса обновлены: ALS={self.weights['als']:.2f}, CF={self.weights['item_cf']:.2f}, Content={self.weights['content']:.2f}")
    def recommend(self, user_id, user_history=None, n=10, min_interactions=3):
        """
        Гибридные рекомендации
        Args:
            user_id: ID пользователя (начиная с 0)
            user_history: список ID товаров из истории пользователя
            n: количество рекомендаций
            min_interactions: минимальное количество взаимодействий для коллаборативной фильтрации
        Returns:
            list: список кортежей (product_id, combined_score)
        """
        recommendations = {}
        # Проверяем, что user_id в пределах матрицы
        if user_id < 0 or user_id >= self.als_model.user_item_matrix.shape[0]:
            return self._get_popular_items(n)
        # Проверяем количество взаимодействий пользователя
        user_item_count = self.als_model.user_item_matrix[user_id].nnz
        # Если достаточно данных, используем коллаборативные методы
        if user_item_count >= min_interactions:
            # ALS рекомендации
            try:
                als_recs = self.als_model.recommend(user_id, n=n*2)
                for product_id, score in als_recs:
                    recommendations[product_id] = recommendations.get(product_id, 0) + \
                        score * self.weights['als']
            except Exception as e:
                print(f"ALS error для пользователя {user_id}: {e}")
            # Item-based CF рекомендации
            try:
                cf_recs = self.item_cf_model.recommend(user_id, n=n*2)
                for product_id, score in cf_recs:
                    recommendations[product_id] = recommendations.get(product_id, 0) + \
                        score * self.weights['item_cf']
            except Exception as e:
                print(f"Item-CF error для пользователя {user_id}: {e}")
        # Content-based рекомендации
        if user_history is not None and len(user_history) > 0:
            try:
                content_recs = self.content_model.recommend_for_user(
                    user_history, n=n*2
                )
                for product_id, score in content_recs:
                    recommendations[product_id] = recommendations.get(product_id, 0) + \
                        score * self.weights['content']
            except Exception as e:
                print(f"Content error для пользователя {user_id}: {e}")
        # Если нет рекомендаций, возвращаем популярные товары
        if not recommendations:
            return self._get_popular_items(n)
        # Сортируем по итоговому скору
        sorted_recs = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_recs[:n]
    def _get_popular_items(self, n=10):
        """
        Популярные товары для холодного старта
        Args:
            n: количество популярных товаров
        Returns:
            list: список кортежей (item_id, popularity_score)
        """
        item_popularity = np.array(
            self.als_model.user_item_matrix.sum(axis=0)
        ).flatten()
        top_items = np.argsort(item_popularity)[::-1][:n]
        return [(item_id, float(item_popularity[item_id])) for item_id in top_items]
    def get_similar_items(self, product_id, n=10):
        """
        Похожие товары (комбинация методов)
        Args:
            product_id: ID товара (начиная с 0)
            n: количество похожих товаров
        Returns:
            list: список кортежей (product_id, combined_score)
        """
        similarities = {}
        # Item-based CF (60% веса)
        try:
            cf_similar = self.item_cf_model.get_similar_items(product_id, n=n*2)
            for pid, score in cf_similar:
                similarities[pid] = similarities.get(pid, 0) + score * 0.6
        except Exception as e:
            print(f"Item-CF error для товара {product_id}: {e}")
        # Content-based (40% веса)
        try:
            content_similar = self.content_model.get_similar_items(product_id, n=n*2)
            for pid, score in content_similar:
                similarities[pid] = similarities.get(pid, 0) + score * 0.4
        except Exception as e:
            print(f"Content error для товара {product_id}: {e}")
        # Сортируем по убыванию схожести
        sorted_similar = sorted(
            similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_similar[:n]
    def predict(self, user_id, product_id):
        """
        Предсказание оценки (для совместимости с evaluator)
        Args:
            user_id: ID пользователя (начиная с 0)
            product_id: ID товара (начиная с 0)
        Returns:
            float: предсказанная оценка
        """
        predictions = []
        weights_sum = 0
        # ALS prediction
        try:
            als_pred = self.als_model.predict(user_id, product_id)
            predictions.append(als_pred * self.weights['als'])
            weights_sum += self.weights['als']
        except:
            pass
        # Item-CF prediction
        try:
            cf_pred = self.item_cf_model.predict(user_id, product_id)
            predictions.append(cf_pred * self.weights['item_cf'])
            weights_sum += self.weights['item_cf']
        except:
            pass
        if weights_sum > 0:
            return sum(predictions) / weights_sum
        return 0.0
import numpy as np
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
class ItemBasedCF:
    def __init__(self, k_neighbors=20):
        self.k_neighbors = k_neighbors
        self.item_similarity_matrix = None
        self.user_item_matrix = None
    def fit(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix
        item_matrix = user_item_matrix.T.toarray()
        self.item_similarity_matrix = cosine_similarity(item_matrix)
        np.fill_diagonal(self.item_similarity_matrix, 0)
        return self
    def get_similar_items(self, product_id, n=10):
        if self.item_similarity_matrix is None:
            return []
        if product_id >= self.item_similarity_matrix.shape[0]:
            return []
        similarities = self.item_similarity_matrix[product_id]
        similar_indices = np.argsort(similarities)[::-1][:n]
        similar_scores = similarities[similar_indices]
        return list(zip(similar_indices.tolist(), similar_scores.tolist()))
    def predict(self, user_id, product_id):
        if user_id >= self.user_item_matrix.shape[0]:
            return 0.0
        user_ratings = self.user_item_matrix[user_id].toarray().flatten()
        rated_indices = np.where(user_ratings > 0)[0]
        if len(rated_indices) == 0:
            return 0.0
        similarities = self.item_similarity_matrix[product_id, rated_indices]
        top_k_idx = np.argsort(similarities)[::-1][:self.k_neighbors]
        top_similarities = similarities[top_k_idx]
        top_ratings = user_ratings[rated_indices[top_k_idx]]
        if np.sum(np.abs(top_similarities)) == 0:
            return 0.0
        prediction = np.sum(top_similarities * top_ratings) / np.sum(np.abs(top_similarities))
        return float(prediction)
    def recommend(self, user_id, n=10, exclude_rated=True):
        if user_id >= self.user_item_matrix.shape[0]:
            return []
        user_ratings = self.user_item_matrix[user_id].toarray().flatten()
        rated_indices = np.where(user_ratings > 0)[0]
        n_items = self.user_item_matrix.shape[1]
        predictions = []
        for product_id in range(n_items):
            if exclude_rated and product_id in rated_indices:
                continue
            score = self.predict(user_id, product_id)
            if score > 0:
                predictions.append((product_id, score))
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]
class ContentBasedRecommender:
    def __init__(self):
        self.product_features = None
        self.similarity_matrix = None
        self.products_df = None
    def fit(self, products_df):
        self.products_df = products_df
        features_list = []
        for idx, product in products_df.iterrows():
            features = {
                'price': product.get('price', 0),
                'material': product.get('material', ''),
                'style': product.get('style', ''),
                'color': product.get('color', ''),
                'manufacturer': product.get('manufacturer', '')
            }
            features_list.append(features)
        n_products = len(products_df)
        feature_vectors = []
        for product in products_df.iterrows():
            p = product[1]
            vector = [
                p.get('price', 0) / 5000,
                hash(p.get('material', '')) % 10,
                hash(p.get('style', '')) % 10,
                hash(p.get('color', '')) % 10,
                hash(p.get('manufacturer', '')) % 10
            ]
            feature_vectors.append(vector)
        feature_vectors = np.array(feature_vectors)
        self.similarity_matrix = cosine_similarity(feature_vectors)
        np.fill_diagonal(self.similarity_matrix, 0)
        return self
    def get_similar_items(self, product_id, n=10):
        if self.similarity_matrix is None:
            return []
        if product_id >= self.similarity_matrix.shape[0]:
            return []
        similarities = self.similarity_matrix[product_id]
        similar_indices = np.argsort(similarities)[::-1][:n]
        similar_scores = similarities[similar_indices]
        return list(zip(similar_indices.tolist(), similar_scores.tolist()))
    def recommend_for_user(self, user_history, n=10):
        if len(user_history) == 0 or self.similarity_matrix is None:
            return []
        user_profile = np.mean(self.similarity_matrix[user_history], axis=0)
        user_profile[user_history] = -1
        top_indices = np.argsort(user_profile)[::-1][:n]
        top_scores = user_profile[top_indices]
        return list(zip(top_indices.tolist(), top_scores.tolist()))
class ALSRecommender:
    def __init__(self, factors=50, regularization=0.01, iterations=15):
        self.model = None
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.user_item_matrix = None
    def fit(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix
        item_user_matrix = user_item_matrix.T.tocsr()
        from implicit.als import AlternatingLeastSquares
        self.model = AlternatingLeastSquares(
            factors=self.factors,
            regularization=self.regularization,
            iterations=self.iterations,
            use_gpu=False
        )
        self.model.fit(item_user_matrix)
        return self
    def recommend(self, user_id, n=10, filter_already_liked=True):
        if self.model is None or user_id >= self.user_item_matrix.shape[0]:
            return self._get_popular_items(n)
        try:
            recommendations = self.model.recommend(
                user_id,
                self.user_item_matrix[user_id],
                N=n,
                filter_already_liked_items=filter_already_liked
            )
            return [(int(item_id), float(score)) for item_id, score in zip(recommendations[0], recommendations[1])]
        except:
            return self._get_popular_items(n)
    def similar_items(self, product_id, n=10):
        if self.model is None:
            return []
        try:
            similar = self.model.similar_items(product_id, N=n)
            return [(int(item_id), float(score)) for item_id, score in zip(similar[0], similar[1])]
        except:
            return []
    def _get_popular_items(self, n=10):
        if self.user_item_matrix is None:
            return []
        item_popularity = np.array(self.user_item_matrix.sum(axis=0)).flatten()
        top_items = np.argsort(item_popularity)[::-1][:n]
        return [(int(item_id), float(item_popularity[item_id])) for item_id in top_items]
class HybridRecommender:
    def __init__(self, als_model, item_cf_model, content_model):
        self.als_model = als_model
        self.item_cf_model = item_cf_model
        self.content_model = content_model
        self.weights = {
            'als': 0.5,
            'item_cf': 0.3,
            'content': 0.2
        }
        self.user_item_matrix = None
        self.products_df = None
    def fit(self, user_item_matrix, products_df):
        self.user_item_matrix = user_item_matrix
        self.products_df = products_df
        self.als_model.fit(user_item_matrix)
        self.item_cf_model.fit(user_item_matrix)
        self.content_model.fit(products_df)
        return self
    def set_weights(self, als_weight, item_cf_weight, content_weight):
        total = als_weight + item_cf_weight + content_weight
        self.weights = {
            'als': als_weight / total,
            'item_cf': item_cf_weight / total,
            'content': content_weight / total
        }
    def recommend(self, user_id, user_history=None, n=10, min_interactions=2):
        recommendations = {}
        if self.user_item_matrix is not None:
            user_item_count = self.user_item_matrix[user_id].nnz if user_id < self.user_item_matrix.shape[0] else 0
        else:
            user_item_count = 0
        if user_item_count >= min_interactions:
            try:
                als_recs = self.als_model.recommend(user_id, n=n*2)
                for product_id, score in als_recs:
                    recommendations[product_id] = recommendations.get(product_id, 0) + score * self.weights['als']
            except Exception as e:
                print(f"ALS error: {e}")
        if user_item_count >= min_interactions:
            try:
                cf_recs = self.item_cf_model.recommend(user_id, n=n*2)
                for product_id, score in cf_recs:
                    recommendations[product_id] = recommendations.get(product_id, 0) + score * self.weights['item_cf']
            except Exception as e:
                print(f"Item-CF error: {e}")
        if user_history is not None and len(user_history) > 0:
            try:
                content_recs = self.content_model.recommend_for_user(user_history, n=n*2)
                for product_id, score in content_recs:
                    if score > 0:
                        recommendations[product_id] = recommendations.get(product_id, 0) + score * self.weights['content']
            except Exception as e:
                print(f"Content error: {e}")
        if not recommendations:
            return self._get_popular_items(n)
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:n]
    def _get_popular_items(self, n=10):
        if self.user_item_matrix is None:
            return []
        item_popularity = np.array(self.user_item_matrix.sum(axis=0)).flatten()
        top_items = np.argsort(item_popularity)[::-1][:n]
        return [(int(item_id), float(item_popularity[item_id])) for item_id in top_items]
    def get_similar_items(self, product_id, n=10):
        similarities = {}
        try:
            als_similar = self.als_model.similar_items(product_id, n=n*2)
            for pid, score in als_similar:
                similarities[pid] = similarities.get(pid, 0) + score * 0.5
        except:
            pass
        try:
            cf_similar = self.item_cf_model.get_similar_items(product_id, n=n*2)
            for pid, score in cf_similar:
                similarities[pid] = similarities.get(pid, 0) + score * 0.3
        except:
            pass
        try:
            content_similar = self.content_model.get_similar_items(product_id, n=n*2)
            for pid, score in content_similar:
                similarities[pid] = similarities.get(pid, 0) + score * 0.2
        except:
            pass
        if not similarities:
            return []
        sorted_similar = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return sorted_similar[:n]
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
class DataPreprocessor:
    def __init__(self):
        self.products_df = None
        self.interactions_df = None
        self.user_item_matrix = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.tfidf = TfidfVectorizer(max_features=50, stop_words='english')
    def load_products_from_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            products_list = json.load(f)
        self.products_df = pd.DataFrame(products_list)
        self.products_df['product_id'] = range(len(self.products_df))
        return self.products_df
    def generate_synthetic_interactions(self, n_users=500, n_interactions=5000):
        if self.products_df is None:
            raise ValueError("Сначала загрузите товары")
        n_products = len(self.products_df)
        interactions = []
        for _ in range(n_interactions):
            user_id = random.randint(1, n_users)
            product_id = random.randint(0, n_products - 1)
            rand = random.random()
            if rand < 0.6:
                interaction_type = 'view'
            elif rand < 0.9:
                interaction_type = 'click'
            else:
                interaction_type = 'purchase'
            interactions.append({
                'user_id': user_id,
                'product_id': product_id,
                'interaction_type': interaction_type,
                'timestamp': datetime.now() - timedelta(days=random.randint(1, 180)),
                'rating': random.randint(1, 5) if interaction_type == 'purchase' else None
            })
        self.interactions_df = pd.DataFrame(interactions)
        return self.interactions_df
    def extract_product_features(self, products_df=None):
        if products_df is None:
            products_df = self.products_df
        if products_df is None:
            raise ValueError("Нет данных о товарах")
        text_data = products_df['name'].fillna('') + ' ' + products_df.get('description', '').fillna('')
        tfidf_matrix = self.tfidf.fit_transform(text_data)
        self.label_encoders['material'] = LabelEncoder()
        self.label_encoders['style'] = LabelEncoder()
        self.label_encoders['color'] = LabelEncoder()
        material_encoded = self.label_encoders['material'].fit_transform(products_df.get('material', ['unknown'] * len(products_df)).fillna('unknown'))
        style_encoded = self.label_encoders['style'].fit_transform(products_df.get('style', ['unknown'] * len(products_df)).fillna('unknown'))
        color_encoded = self.label_encoders['color'].fit_transform(products_df.get('color', ['unknown'] * len(products_df)).fillna('unknown'))
        prices = products_df[['price']].fillna(0).values.astype(float)
        price_normalized = self.scaler.fit_transform(prices)
        from scipy.sparse import hstack, csr_matrix
        features = hstack([
            tfidf_matrix,
            csr_matrix(material_encoded.reshape(-1, 1)),
            csr_matrix(style_encoded.reshape(-1, 1)),
            csr_matrix(color_encoded.reshape(-1, 1)),
            csr_matrix(price_normalized)
        ])
        return features
    def create_user_item_matrix(self):
        if self.interactions_df is None:
            raise ValueError("Сначала загрузите взаимодействия")
        from scipy.sparse import csr_matrix
        interaction_weights = {
            'purchase': 5,
            'click': 3,
            'view': 1
        }
        interactions_df = self.interactions_df.copy()
        interactions_df['weight'] = interactions_df['interaction_type'].map(interaction_weights)
        user_item_data = interactions_df.groupby(['user_id', 'product_id'])['weight'].max().reset_index()
        user_ids = user_item_data['user_id'].values - 1
        product_ids = user_item_data['product_id'].values
        weights = user_item_data['weight'].values
        max_user_id = user_ids.max() + 1
        n_products = len(self.products_df)
        self.user_item_matrix = csr_matrix(
            (weights, (user_ids, product_ids)),
            shape=(max_user_id, n_products)
        )
        return self.user_item_matrix
    def split_train_test(self, test_size=0.2):
        if self.interactions_df is None:
            raise ValueError("Сначала загрузите взаимодействия")
        interactions_sorted = self.interactions_df.sort_values('timestamp')
        split_idx = int(len(interactions_sorted) * (1 - test_size))
        train = interactions_sorted.iloc[:split_idx].reset_index(drop=True)
        test = interactions_sorted.iloc[split_idx:].reset_index(drop=True)
        return train, test
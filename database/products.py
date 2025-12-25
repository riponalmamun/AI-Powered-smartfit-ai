import json
from pathlib import Path
from typing import List, Dict, Optional
from config import settings

class ProductDatabase:
    def __init__(self):
        self.products_file = settings.BASE_DIR / "products.json"
        self.products = self._load_products()
    
    def _load_products(self) -> List[Dict]:
        if self.products_file.exists():
            with open(self.products_file, 'r') as f:
                data = json.load(f)
                return data.get('products', [])
        else:
            return self._create_sample_products()
    
    def _create_sample_products(self) -> List[Dict]:
        sample_products = [
            {
                "product_id": "prod_001",
                "name": "Blue Casual T-Shirt",
                "category": "tshirt",
                "gender": "male",
                "age_groups": ["teens", "young_adults", "adults"],
                "style": "casual",
                "body_types_suited": ["slim", "athletic", "average"],
                "colors": ["blue"],
                "sizes": ["S", "M", "L", "XL"],
                "price": 599,
                "image_path": "products/male/young_adults/tshirt_001.png",
                "popularity_score": 85
            },
            {
                "product_id": "prod_002",
                "name": "Black Formal Shirt",
                "category": "shirt",
                "gender": "male",
                "age_groups": ["young_adults", "adults"],
                "style": "formal",
                "body_types_suited": ["slim", "athletic", "average"],
                "colors": ["black"],
                "sizes": ["S", "M", "L", "XL"],
                "price": 999,
                "image_path": "products/male/adults/shirt_001.png",
                "popularity_score": 75
            },
            {
                "product_id": "prod_003",
                "name": "Red Floral Dress",
                "category": "dress",
                "gender": "female",
                "age_groups": ["teens", "young_adults"],
                "style": "casual",
                "body_types_suited": ["slim", "average"],
                "colors": ["red"],
                "sizes": ["S", "M", "L"],
                "price": 1299,
                "image_path": "products/female/young_adults/dress_001.png",
                "popularity_score": 90
            },
            {
                "product_id": "prod_004",
                "name": "White Casual Top",
                "category": "top",
                "gender": "female",
                "age_groups": ["teens", "young_adults", "adults"],
                "style": "casual",
                "body_types_suited": ["slim", "athletic", "average", "plus_size"],
                "colors": ["white"],
                "sizes": ["S", "M", "L", "XL"],
                "price": 699,
                "image_path": "products/female/young_adults/top_001.png",
                "popularity_score": 80
            },
            {
                "product_id": "prod_005",
                "name": "Gray Hoodie",
                "category": "hoodie",
                "gender": "male",
                "age_groups": ["teens", "young_adults"],
                "style": "sporty",
                "body_types_suited": ["slim", "athletic", "average"],
                "colors": ["gray"],
                "sizes": ["M", "L", "XL"],
                "price": 1499,
                "image_path": "products/male/teens/hoodie_001.png",
                "popularity_score": 88
            }
        ]
        
        self._save_products(sample_products)
        return sample_products
    
    def _save_products(self, products: List[Dict]):
        with open(self.products_file, 'w') as f:
            json.dump({'products': products}, f, indent=2)
    
    def get_all_products(self) -> List[Dict]:
        return self.products
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        for product in self.products:
            if product['product_id'] == product_id:
                return product
        return None
    
    def search_products(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            if (query_lower in product['name'].lower() or
                query_lower in product['category'].lower() or
                query_lower in product['style'].lower()):
                results.append(product)
        
        return results
    
    def add_product(self, product: Dict) -> bool:
        if self.get_product_by_id(product['product_id']):
            return False
        
        self.products.append(product)
        self._save_products(self.products)
        return True
    
    def update_product(self, product_id: str, updates: Dict) -> bool:
        for i, product in enumerate(self.products):
            if product['product_id'] == product_id:
                self.products[i].update(updates)
                self._save_products(self.products)
                return True
        return False
    
    def delete_product(self, product_id: str) -> bool:
        original_length = len(self.products)
        self.products = [p for p in self.products if p['product_id'] != product_id]
        
        if len(self.products) < original_length:
            self._save_products(self.products)
            return True
        return False

product_db = ProductDatabase()
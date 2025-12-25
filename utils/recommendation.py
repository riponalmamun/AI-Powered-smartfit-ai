from typing import List, Dict
from config import settings

class RecommendationEngine:
    def __init__(self):
        self.style_weight = settings.STYLE_WEIGHT
        self.color_weight = settings.COLOR_WEIGHT
        self.body_type_weight = settings.BODY_TYPE_WEIGHT
    
    def filter_products(self, products: List[Dict], user_profile: Dict) -> List[Dict]:
        filtered = []
        
        user_gender = user_profile.get('gender', 'male')
        user_age_group = user_profile.get('age_group', 'young_adults')
        user_body_type = user_profile.get('body_type', 'average')
        
        for product in products:
            if product.get('gender') != user_gender:
                continue
            
            if user_age_group not in product.get('age_groups', []):
                continue
            
            filtered.append(product)
        
        return filtered
    
    def rank_products(self, products: List[Dict], user_profile: Dict) -> List[Dict]:
        user_preferences = user_profile.get('preferences', {})
        style_prefs = user_preferences.get('styles', {})
        color_prefs = user_preferences.get('colors', {})
        user_body_type = user_profile.get('body_type', 'average')
        
        for product in products:
            score = 0
            
            product_style = product.get('style', 'casual')
            if product_style in style_prefs:
                score += style_prefs[product_style] * self.style_weight
            
            product_colors = product.get('colors', [])
            for color in product_colors:
                if color in color_prefs:
                    score += color_prefs[color] * self.color_weight
            
            body_types_suited = product.get('body_types_suited', [])
            if user_body_type in body_types_suited:
                score += 10 * self.body_type_weight
            
            product['recommendation_score'] = score
        
        sorted_products = sorted(
            products, 
            key=lambda x: x.get('recommendation_score', 0), 
            reverse=True
        )
        
        return sorted_products
    
    def get_personalized_suggestions(self, all_products: List[Dict], user_profile: Dict, limit: int = None) -> List[Dict]:
        filtered = self.filter_products(all_products, user_profile)
        
        ranked = self.rank_products(filtered, user_profile)
        
        if limit:
            return ranked[:limit]
        
        return ranked[:settings.TOP_SUGGESTIONS_COUNT]
    
    def update_user_preferences(self, user_profile: Dict, interaction: Dict) -> Dict:
        if 'preferences' not in user_profile:
            user_profile['preferences'] = {
                'styles': {},
                'colors': {}
            }
        
        product_style = interaction.get('product_style')
        if product_style:
            current = user_profile['preferences']['styles'].get(product_style, 0)
            user_profile['preferences']['styles'][product_style] = current + 1
        
        product_colors = interaction.get('product_colors', [])
        for color in product_colors:
            current = user_profile['preferences']['colors'].get(color, 0)
            user_profile['preferences']['colors'][color] = current + 1
        
        return user_profile
    
    def get_similar_products(self, product: Dict, all_products: List[Dict], limit: int = 5) -> List[Dict]:
        similar = []
        
        product_style = product.get('style')
        product_colors = product.get('colors', [])
        product_category = product.get('category')
        
        for p in all_products:
            if p.get('product_id') == product.get('product_id'):
                continue
            
            similarity_score = 0
            
            if p.get('style') == product_style:
                similarity_score += 3
            
            if p.get('category') == product_category:
                similarity_score += 2
            
            common_colors = set(p.get('colors', [])) & set(product_colors)
            similarity_score += len(common_colors)
            
            if similarity_score > 0:
                p_copy = p.copy()
                p_copy['similarity_score'] = similarity_score
                similar.append(p_copy)
        
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar[:limit]
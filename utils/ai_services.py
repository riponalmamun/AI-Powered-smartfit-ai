import os
import base64
import requests
from typing import Optional, Dict, List
from config import settings

class OpenAIService:
    """
    OpenAI API integration for advanced features
    Paid service - requires API key
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"
        self.enabled = settings.ENABLE_OPENAI and bool(self.api_key)
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def generate_style_description(self, product: Dict) -> Optional[str]:
        """Generate AI-powered product description"""
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Generate a compelling fashion description for this product:
            Name: {product.get('name')}
            Style: {product.get('style')}
            Colors: {', '.join(product.get('colors', []))}
            Category: {product.get('category')}
            
            Write a short, appealing description (2-3 sentences) that would help customers decide to buy."""
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a fashion expert writing product descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 150
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
        except Exception as e:
            print(f"OpenAI error: {str(e)}")
            return None
    
    def get_outfit_suggestions(self, product: Dict, user_profile: Dict) -> Optional[List[str]]:
        """Get AI-powered outfit pairing suggestions"""
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Suggest 3 items that would pair well with this product:
            Product: {product.get('name')}
            Style: {product.get('style')}
            Color: {', '.join(product.get('colors', []))}
            
            User Profile:
            Gender: {user_profile.get('gender')}
            Age Group: {user_profile.get('age_group')}
            Body Type: {user_profile.get('body_type')}
            
            List 3 specific clothing items that would complete the outfit."""
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a fashion stylist providing outfit suggestions."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 100
                },
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                suggestions = [s.strip() for s in content.split('\n') if s.strip()]
                return suggestions[:3]
            return None
        except Exception as e:
            print(f"OpenAI error: {str(e)}")
            return None


class HuggingFaceService:
    """
    Hugging Face API integration
    Free tier available with rate limits
    """
    
    def __init__(self):
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.base_url = "https://api-inference.huggingface.co/models"
        self.enabled = bool(self.api_key)
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def generate_product_tags(self, product_name: str, product_style: str) -> Optional[List[str]]:
        """Generate relevant tags for products using HF"""
        if not self.enabled:
            return None
        
        try:
            model_url = f"{self.base_url}/facebook/bart-large-mnli"
            
            response = requests.post(
                model_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "inputs": f"{product_name} {product_style}",
                    "parameters": {"candidate_labels": ["trendy", "classic", "elegant", "casual", "sporty", "formal"]}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('labels', [])[:3]
            return None
        except Exception as e:
            print(f"HuggingFace error: {str(e)}")
            return None
    
    def analyze_image_style(self, image_path: str) -> Optional[Dict]:
        """Analyze clothing style from image"""
        if not self.enabled:
            return None
        
        try:
            model_url = f"{self.base_url}/google/vit-base-patch16-224"
            
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            response = requests.post(
                model_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=image_data,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"HuggingFace error: {str(e)}")
            return None


class ReplicateService:
    """
    Replicate API integration
    Free tier with credits available
    """
    
    def __init__(self):
        self.api_token = settings.REPLICATE_API_TOKEN
        self.base_url = "https://api.replicate.com/v1"
        self.enabled = bool(self.api_token)
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def enhance_tryon_image(self, image_path: str) -> Optional[str]:
        """Enhance try-on result image quality"""
        if not self.enabled:
            return None
        
        try:
            # Using Real-ESRGAN for image enhancement
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            response = requests.post(
                f"{self.base_url}/predictions",
                headers={
                    "Authorization": f"Token {self.api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
                    "input": {
                        "image": f"data:image/jpeg;base64,{image_data}",
                        "scale": 2
                    }
                },
                timeout=30
            )
            
            if response.status_code == 201:
                prediction = response.json()
                return prediction.get('urls', {}).get('get')
            return None
        except Exception as e:
            print(f"Replicate error: {str(e)}")
            return None


# Free Alternative Services

class FreeStyleAnalyzer:
    """
    Free alternative for basic style analysis
    No API key needed
    """
    
    @staticmethod
    def analyze_style_from_metadata(product: Dict) -> Dict:
        """Analyze product style from metadata"""
        
        style_descriptions = {
            'casual': 'Perfect for everyday wear. Comfortable and relaxed.',
            'formal': 'Elegant and professional. Ideal for formal occasions.',
            'ethnic': 'Traditional and culturally rich. Perfect for special events.',
            'sporty': 'Athletic and active. Great for workouts and sports.',
            'party': 'Stylish and trendy. Perfect for parties and social events.'
        }
        
        style = product.get('style', 'casual')
        
        return {
            'style': style,
            'description': style_descriptions.get(style, 'Stylish and versatile.'),
            'tags': FreeStyleAnalyzer._generate_tags(product),
            'occasion': FreeStyleAnalyzer._suggest_occasion(style)
        }
    
    @staticmethod
    def _generate_tags(product: Dict) -> List[str]:
        """Generate tags based on product attributes"""
        tags = []
        
        style = product.get('style', '')
        if style:
            tags.append(style)
        
        colors = product.get('colors', [])
        if colors:
            tags.extend(colors[:2])
        
        category = product.get('category', '')
        if category:
            tags.append(category)
        
        return tags[:5]
    
    @staticmethod
    def _suggest_occasion(style: str) -> List[str]:
        """Suggest occasions for style"""
        occasions = {
            'casual': ['daily wear', 'shopping', 'casual outings'],
            'formal': ['office', 'meetings', 'formal events'],
            'ethnic': ['festivals', 'weddings', 'cultural events'],
            'sporty': ['gym', 'sports', 'outdoor activities'],
            'party': ['parties', 'nightlife', 'celebrations']
        }
        
        return occasions.get(style, ['any occasion'])


# Initialize services
openai_service = OpenAIService()
huggingface_service = HuggingFaceService()
replicate_service = ReplicateService()
free_style_analyzer = FreeStyleAnalyzer()
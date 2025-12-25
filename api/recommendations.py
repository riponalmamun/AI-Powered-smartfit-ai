from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict  # Added Dict here
from config import settings
from utils.recommendation import RecommendationEngine
from utils.ai_services import openai_service, huggingface_service, free_style_analyzer
from database.products import product_db
from database.users import user_db

router = APIRouter()
recommendation_engine = RecommendationEngine()

class InteractionRequest(BaseModel):
    photo_id: str
    product_id: str
    action: str
    duration_seconds: Optional[int] = 0

@router.get("/products")
async def get_all_products(
    gender: Optional[str] = None,
    style: Optional[str] = None,
    limit: Optional[int] = None
):
    products = product_db.get_all_products()
    
    if gender:
        products = [p for p in products if p.get('gender') == gender]
    
    if style:
        products = [p for p in products if p.get('style') == style]
    
    if limit:
        products = products[:limit]
    
    return {
        "total": len(products),
        "products": products
    }

@router.get("/products/{product_id}")
async def get_product(product_id: str, enhance: bool = False):
    product = product_db.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Add AI-enhanced information if requested
    if enhance:
        product_copy = product.copy()
        
        # Try OpenAI first (paid)
        if openai_service.is_enabled():
            ai_description = openai_service.generate_style_description(product)
            if ai_description:
                product_copy['ai_description'] = ai_description
        
        # Try HuggingFace for tags (free)
        if huggingface_service.is_enabled():
            tags = huggingface_service.generate_product_tags(
                product.get('name', ''),
                product.get('style', '')
            )
            if tags:
                product_copy['ai_tags'] = tags
        
        # Always add free style analysis
        style_analysis = free_style_analyzer.analyze_style_from_metadata(product)
        product_copy['style_analysis'] = style_analysis
        
        return product_copy
    
    return product

@router.get("/products/search")
async def search_products(query: str = Query(..., min_length=1)):
    results = product_db.search_products(query)
    
    return {
        "query": query,
        "total": len(results),
        "results": results
    }

@router.get("/smart-suggestions")
async def get_smart_suggestions(
    photo_id: str,
    limit: Optional[int] = settings.TOP_SUGGESTIONS_COUNT
):
    user_id = f"user_{photo_id}"
    user_profile = user_db.get_user_profile(user_id)
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found. Please analyze photo first.")
    
    all_products = product_db.get_all_products()
    
    suggestions = recommendation_engine.get_personalized_suggestions(
        all_products,
        user_profile.get('detected_profile', {}),
        limit
    )
    
    return {
        "user_id": user_id,
        "user_profile": {
            "gender": user_profile.get('detected_profile', {}).get('gender'),
            "age_group": user_profile.get('detected_profile', {}).get('age_group'),
            "body_type": user_profile.get('detected_profile', {}).get('body_type')
        },
        "total_suggestions": len(suggestions),
        "suggestions": suggestions
    }

@router.get("/recommended-for-you")
async def get_personalized_recommendations(
    photo_id: str,
    limit: Optional[int] = 20
):
    user_id = f"user_{photo_id}"
    user_profile = user_db.get_user_profile(user_id)
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    all_products = product_db.get_all_products()
    
    combined_profile = {
        **user_profile.get('detected_profile', {}),
        'preferences': user_profile.get('preferences', {})
    }
    
    recommendations = recommendation_engine.get_personalized_suggestions(
        all_products,
        combined_profile,
        limit
    )
    
    return {
        "user_id": user_id,
        "based_on": {
            "total_interactions": len(user_profile.get('interaction_history', [])),
            "style_preferences": user_profile.get('preferences', {}).get('styles', {}),
            "color_preferences": user_profile.get('preferences', {}).get('colors', {})
        },
        "recommendations": recommendations
    }

@router.post("/track-interaction")
async def track_interaction(interaction: InteractionRequest):
    user_id = f"user_{interaction.photo_id}"
    
    user_profile = user_db.get_user_profile(user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    product = product_db.get_product_by_id(interaction.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    interaction_data = {
        'action': interaction.action,
        'product_id': interaction.product_id,
        'product_style': product.get('style'),
        'product_colors': product.get('colors', []),
        'duration_seconds': interaction.duration_seconds
    }
    
    user_db.add_interaction(user_id, interaction_data)
    
    updated_profile = recommendation_engine.update_user_preferences(
        user_profile,
        interaction_data
    )
    
    user_db.update_preferences(user_id, updated_profile['preferences'])
    
    return {
        "status": "success",
        "message": "Interaction tracked successfully",
        "updated_preferences": updated_profile['preferences']
    }

@router.get("/similar-products/{product_id}")
async def get_similar_products(product_id: str, limit: int = 5):
    product = product_db.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    all_products = product_db.get_all_products()
    
    similar = recommendation_engine.get_similar_products(
        product,
        all_products,
        limit
    )
    
    return {
        "product_id": product_id,
        "product_name": product.get('name'),
        "similar_products": similar
    }

class SaveFavoriteRequest(BaseModel):
    photo_id: str
    tryon_id: str
    product_id: str

@router.post("/save-favorite")
async def save_favorite(request: SaveFavoriteRequest):
    user_id = f"user_{request.photo_id}"
    
    favorite_data = {
        'tryon_id': request.tryon_id,
        'product_id': request.product_id
    }
    
    success = user_db.add_favorite(user_id, favorite_data)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "message": "Favorite saved successfully"
    }

@router.get("/favorites/{photo_id}")
async def get_favorites(photo_id: str):
    user_id = f"user_{photo_id}"
    favorites = user_db.get_user_favorites(user_id)
    
    return {
        "user_id": user_id,
        "total_favorites": len(favorites),
        "favorites": favorites
    }

@router.get("/history/{photo_id}")
async def get_user_history(photo_id: str):
    user_id = f"user_{photo_id}"
    history = user_db.get_user_history(user_id)
    
    return {
        "user_id": user_id,
        "total_interactions": len(history),
        "history": history
    }

@router.get("/outfit-suggestions/{product_id}")
async def get_outfit_suggestions(product_id: str, photo_id: Optional[str] = None):
    """Get AI-powered outfit pairing suggestions"""
    
    product = product_db.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    suggestions = {
        "product": product,
        "pairing_suggestions": []
    }
    
    # Get user profile if available
    user_profile = {}
    if photo_id:
        user_id = f"user_{photo_id}"
        user_data = user_db.get_user_profile(user_id)
        if user_data:
            user_profile = user_data.get('detected_profile', {})
    
    # Try OpenAI for advanced suggestions
    if openai_service.is_enabled() and user_profile:
        ai_suggestions = openai_service.get_outfit_suggestions(product, user_profile)
        if ai_suggestions:
            suggestions['pairing_suggestions'] = ai_suggestions
            suggestions['source'] = 'openai'
            return suggestions
    
    # Fallback to rule-based suggestions
    suggestions['pairing_suggestions'] = _get_rule_based_suggestions(product)
    suggestions['source'] = 'rule_based'
    
    return suggestions

def _get_rule_based_suggestions(product: Dict) -> List[str]:
    """Rule-based outfit suggestions (free)"""
    
    category = product.get('category', '').lower()
    style = product.get('style', '').lower()
    colors = product.get('colors', [])
    
    suggestions = []
    
    if category == 'tshirt':
        suggestions = [
            "Pair with slim-fit jeans for a casual look",
            "Add a denim jacket for layering",
            "Complete with sneakers or casual shoes"
        ]
    elif category == 'shirt':
        suggestions = [
            "Pair with formal trousers for office wear",
            "Add a blazer for a professional look",
            "Complete with leather shoes"
        ]
    elif category == 'dress':
        suggestions = [
            "Pair with heels for an elegant look",
            "Add a clutch purse to complete the outfit",
            "Consider a light jacket for cooler weather"
        ]
    elif category == 'jeans':
        suggestions = [
            "Pair with a casual t-shirt or shirt",
            "Add sneakers or boots",
            "Consider a belt to complete the look"
        ]
    else:
        suggestions = [
            f"Pair with complementary {style} items",
            "Add accessories to enhance the look",
            "Complete with appropriate footwear"
        ]
    
    return suggestions

@router.get("/api-status")
async def get_api_status():
    """Check which AI services are enabled"""
    
    return {
        "openai": {
            "enabled": openai_service.is_enabled(),
            "features": ["product descriptions", "outfit suggestions"] if openai_service.is_enabled() else []
        },
        "huggingface": {
            "enabled": huggingface_service.is_enabled(),
            "features": ["product tags", "style analysis"] if huggingface_service.is_enabled() else []
        },
        "free_services": {
            "enabled": True,
            "features": ["basic style analysis", "rule-based suggestions"]
        }
    }
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import time
import uuid
from typing import List
from config import settings
from utils.virtual_tryon import VirtualTryOn
from database.products import product_db
from database.users import user_db

router = APIRouter()
virtual_tryon = VirtualTryOn()

class TryOnRequest(BaseModel):
    photo_id: str
    product_id: str

class TryOnResponse(BaseModel):
    tryon_id: str
    status: str
    image_url: str
    processing_time: float
    quality_score: float

@router.post("/try-on", response_model=TryOnResponse)
async def try_on(request: TryOnRequest):
    start_time = time.time()
    
    photo_files = list(settings.UPLOADS_DIR.glob(f"{request.photo_id}.*"))
    if not photo_files:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    user_photo_path = photo_files[0]
    
    product = product_db.get_product_by_id(request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_image_path = settings.BASE_DIR / product['image_path']
    if not product_image_path.exists():
        raise HTTPException(status_code=404, detail="Product image not found")
    
    tryon_id = f"tryon_{uuid.uuid4().hex[:12]}"
    output_filename = f"{tryon_id}.jpg"
    output_path = settings.OUTPUTS_DIR / output_filename
    
    result = virtual_tryon.process_tryon(
        user_photo_path,
        product_image_path,
        output_path
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=f"Try-on processing failed: {result.get('error', 'Unknown error')}"
        )
    
    user_id = f"user_{request.photo_id}"
    interaction = {
        'action': 'tried_on',
        'product_id': request.product_id,
        'product_style': product.get('style'),
        'product_colors': product.get('colors', []),
        'tryon_id': tryon_id
    }
    user_db.add_interaction(user_id, interaction)
    
    processing_time = time.time() - start_time
    
    return {
        "tryon_id": tryon_id,
        "status": "success",
        "image_url": f"/outputs/{output_filename}",
        "processing_time": round(processing_time, 2),
        "quality_score": result.get('quality_score', 0.8)
    }

class MultipleTryOnRequest(BaseModel):
    photo_id: str
    product_ids: List[str]

@router.post("/try-on/multiple")
async def try_on_multiple(request: MultipleTryOnRequest):
    results = []
    
    for product_id in request.product_ids:
        try:
            single_request = TryOnRequest(
                photo_id=request.photo_id,
                product_id=product_id
            )
            result = await try_on(single_request)
            results.append(result)
        except Exception as e:
            results.append({
                "product_id": product_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "total": len(request.product_ids),
        "successful": len([r for r in results if r.get('status') == 'success']),
        "results": results
    }

@router.get("/tryon/{tryon_id}")
async def get_tryon_result(tryon_id: str):
    output_files = list(settings.OUTPUTS_DIR.glob(f"{tryon_id}.*"))
    
    if not output_files:
        raise HTTPException(status_code=404, detail="Try-on result not found")
    
    output_file = output_files[0]
    
    return {
        "tryon_id": tryon_id,
        "image_url": f"/outputs/{output_file.name}",
        "exists": True
    }
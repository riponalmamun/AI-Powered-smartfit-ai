from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import shutil
from config import settings
from utils.image_processing import ImageProcessor

router = APIRouter()
image_processor = ImageProcessor()

@router.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Allowed formats: {', '.join(settings.ALLOWED_IMAGE_FORMATS)}"
        )
    
    photo_id = f"photo_{uuid.uuid4().hex[:12]}"
    photo_filename = f"{photo_id}{file_extension}"
    photo_path = settings.UPLOADS_DIR / photo_filename
    
    with open(photo_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    is_valid, message = image_processor.validate_image(photo_path)
    if not is_valid:
        photo_path.unlink()
        raise HTTPException(status_code=400, detail=message)
    
    quality_info = image_processor.get_image_quality_score(photo_path)
    
    return {
        "photo_id": photo_id,
        "filename": photo_filename,
        "path": f"/uploads/{photo_filename}",
        "status": "success",
        "quality": quality_info,
        "message": "Photo uploaded successfully"
    }

@router.delete("/photo/{photo_id}")
async def delete_photo(photo_id: str):
    photo_files = list(settings.UPLOADS_DIR.glob(f"{photo_id}.*"))
    
    if not photo_files:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    for photo_file in photo_files:
        photo_file.unlink()
    
    return {
        "status": "success",
        "message": "Photo deleted successfully",
        "photo_id": photo_id
    }

@router.get("/photo/{photo_id}")
async def get_photo_info(photo_id: str):
    photo_files = list(settings.UPLOADS_DIR.glob(f"{photo_id}.*"))
    
    if not photo_files:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    photo_path = photo_files[0]
    quality_info = image_processor.get_image_quality_score(photo_path)
    
    return {
        "photo_id": photo_id,
        "filename": photo_path.name,
        "path": f"/uploads/{photo_path.name}",
        "quality": quality_info,
        "exists": True
    }
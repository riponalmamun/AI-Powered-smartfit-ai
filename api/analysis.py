from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import time
from config import settings
from utils.ai_models import GenderAgeDetector, BodyTypeDetector
from database.users import user_db

router = APIRouter()
gender_age_detector = GenderAgeDetector()
body_type_detector = BodyTypeDetector()

class AnalysisResponse(BaseModel):
    photo_id: str
    user_profile: dict
    processing_time: float

@router.post("/analyze-user", response_model=AnalysisResponse)
async def analyze_user(photo_id: str):
    start_time = time.time()
    
    photo_files = list(settings.UPLOADS_DIR.glob(f"{photo_id}.*"))
    
    if not photo_files:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    photo_path = photo_files[0]
    
    gender_age_result = gender_age_detector.detect(photo_path)
    
    body_type_result = body_type_detector.detect(photo_path)
    
    user_profile = {
        'gender': gender_age_result['gender'],
        'gender_confidence': gender_age_result['gender_confidence'],
        'age': gender_age_result['age'],
        'age_group': gender_age_result['age_group'],
        'body_type': body_type_result['body_type'],
        'body_measurements': body_type_result['body_measurements'],
        'pose_quality': body_type_result['pose_quality'],
        'detection_success': {
            'gender_age': gender_age_result['success'],
            'body_type': body_type_result['success']
        }
    }
    
    user_id = f"user_{photo_id}"
    existing_user = user_db.get_user_profile(user_id)
    
    if not existing_user:
        user_db.create_user_profile(user_id, user_profile)
    else:
        user_db.update_user_profile(user_id, {
            'detected_profile': user_profile
        })
    
    processing_time = time.time() - start_time
    
    return {
        "photo_id": photo_id,
        "user_profile": user_profile,
        "processing_time": round(processing_time, 2)
    }

@router.get("/user-profile/{photo_id}")
async def get_user_profile(photo_id: str):
    user_id = f"user_{photo_id}"
    user_profile = user_db.get_user_profile(user_id)
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return user_profile
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Project Info
    PROJECT_NAME = "SmartFit AI"
    VERSION = "1.0.0"
    DESCRIPTION = "Intelligent Virtual Try-On System"
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent
    UPLOADS_DIR = BASE_DIR / "uploads"
    PRODUCTS_DIR = BASE_DIR / "products"
    OUTPUTS_DIR = BASE_DIR / "outputs"
    MODELS_DIR = BASE_DIR / os.getenv("MODEL_CACHE_DIR", "models")
    USER_DATA_DIR = BASE_DIR / "user_data"
    
    # Create directories if not exist
    UPLOADS_DIR.mkdir(exist_ok=True)
    PRODUCTS_DIR.mkdir(exist_ok=True)
    OUTPUTS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    USER_DATA_DIR.mkdir(exist_ok=True)
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
    
    # Feature Flags
    ENABLE_OPENAI = os.getenv("ENABLE_OPENAI", "False").lower() == "true"
    ENABLE_STYLE_RECOMMENDATIONS = os.getenv("ENABLE_STYLE_RECOMMENDATIONS", "True").lower() == "true"
    ENABLE_BODY_ANALYSIS = os.getenv("ENABLE_BODY_ANALYSIS", "True").lower() == "true"
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"
    
    # File Upload Settings
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_IMAGE_SIZE_MB", "10")) * 1024 * 1024
    ALLOWED_IMAGE_FORMATS = [f".{fmt}" for fmt in os.getenv("ALLOWED_IMAGE_FORMATS", "jpg,jpeg,png").split(",")]
    
    # AI Model Settings
    DEEPFACE_BACKEND = os.getenv("DEEPFACE_BACKEND", "opencv")
    GENDER_DETECTION_THRESHOLD = 0.7
    AGE_DETECTION_THRESHOLD = 0.7
    POSE_DETECTION_CONFIDENCE = 0.5
    
    # Product Categories
    GENDER_CATEGORIES = ["male", "female"]
    AGE_GROUPS = ["kids", "teens", "young_adults", "adults"]
    STYLE_CATEGORIES = ["casual", "formal", "ethnic", "sporty", "party"]
    BODY_TYPES = ["slim", "athletic", "average", "plus_size"]
    
    # Recommendation Settings
    TOP_SUGGESTIONS_COUNT = 50
    STYLE_WEIGHT = 2.0
    COLOR_WEIGHT = 1.0
    BODY_TYPE_WEIGHT = 1.5
    
    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "smartfit.log")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartfit.db")

settings = Settings()
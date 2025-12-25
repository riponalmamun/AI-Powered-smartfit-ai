from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from api import upload, analysis, tryon, recommendations

# Initialize FastAPI app with better description
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## 🎯 SmartFit AI - Virtual Try-On System

### Features:
* **Photo Upload** - Upload user photos with quality analysis
* **AI Analysis** - Detect gender, age, and body type
* **Virtual Try-On** - Try clothes virtually on your photo
* **Smart Recommendations** - Get personalized product suggestions
* **Product Catalog** - Browse and search products
* **User Features** - Save favorites, track interactions

### Workflow:
1. Upload a photo (`POST /api/upload-photo`)
2. Analyze the user (`POST /api/analyze-user`)
3. Get smart suggestions (`GET /api/smart-suggestions`)
4. Try on products (`POST /api/try-on`)
5. Save favorites and track interactions
    """
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/products", StaticFiles(directory=str(settings.PRODUCTS_DIR)), name="products")
app.mount("/outputs", StaticFiles(directory=str(settings.OUTPUTS_DIR)), name="outputs")

# Include API routers with organized tags and numbering
app.include_router(
    upload.router, 
    prefix="/api", 
    tags=["1️⃣ Upload & Photos"]
)

app.include_router(
    analysis.router, 
    prefix="/api", 
    tags=["2️⃣ AI Analysis"]
)

app.include_router(
    tryon.router, 
    prefix="/api", 
    tags=["3️⃣ Virtual Try-On"]
)

app.include_router(
    recommendations.router,
    prefix="/api",
    tags=["4️⃣ Products & Recommendations"]
)

@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
        "endpoints": {
            "upload": "/api/upload-photo",
            "analyze": "/api/analyze-user",
            "try_on": "/api/try-on",
            "suggestions": "/api/smart-suggestions"
        }
    }

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime": "running",
        "features": {
            "photo_upload": True,
            "ai_analysis": True,
            "virtual_tryon": True,
            "recommendations": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
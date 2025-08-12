from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.content import router as content_router
from app.config import settings
from app.db import get_users_collection
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Catalyst Career AI",
    description="AI-powered career guidance platform with RAG and CrewAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
frontend_env = os.getenv("FRONTEND_URL")
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "http://localhost:5173",  # Vite dev server (admin-dashboard)
    "http://127.0.0.1:5173",
    "https://localhost:5173",
    "https://catalyst-career-ai-frontend.vercel.app",  # Production frontend
    "https://catalyst-career-ai-frontend.vercel.app/",  # With trailing slash
    "https://catalystcareers.in",  # Primary site
    "https://catalystcareers.in/",  # With trailing slash
    "https://www.catalystcareers.in",  # www subdomain
    "https://www.catalystcareers.in/",  # With trailing slash
    "https://admin.catalystcareers.in",  # Admin dashboard
    "https://admin.catalystcareers.in/",  # Admin dashboard with trailing slash
]

# Add environment variable frontend URL if provided
if frontend_env:
    allowed_origins.append(frontend_env)

# Log the allowed origins for debugging
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Allow localhost, vercel deployments, and any subdomain of catalystcareers.in (including admin)
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https?://[a-z0-9-]+\.vercel\.app$|^https?://([a-z0-9-]+\.)?catalystcareers\.in$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "./data",
        "./data/career_documents", 
        "./data/vector_db"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

# Initialize directories on startup
create_directories()

# Include API routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(content_router, prefix="/api", tags=["content"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "message": "🚀 Catalyst Career AI is running!",
        "version": "1.0.0",
        "description": "AI-powered career guidance with RAG and CrewAI",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/api/health", 
            "docs": "/docs",
            "agents": "/api/agent-info"
        },
        "status": "operational"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "An unexpected error occurred. Please try again later.",
            "type": "internal_server_error"
        }
    )

# Startup event - Updated for older FastAPI patterns
@app.on_event("startup")
async def startup_event():
    """Startup event to initialize services"""
    logger.info("🚀 Starting Catalyst Career AI...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Check if API key is configured
    if not settings.GOOGLE_API_KEY:
        # Do NOT crash the app if the key is missing; auth/admin endpoints should still work.
        # Chat endpoints will gracefully report unavailability.
        logger.warning("⚠️ GOOGLE_API_KEY not configured; chat features may be unavailable")
    else:
        logger.info("✅ Google API Key configured")
    
    # Test basic imports to catch early errors
    try:
        from app.services.crew_service import CrewService
        from app.services.rag_service import RAGService
        logger.info("✅ Services imported successfully")
    except Exception as e:
        logger.error(f"❌ Error importing services: {e}")
        # Don't raise here, let it fail gracefully on first request
    
    logger.info("✅ Catalyst Career AI started successfully!")

    # Ensure DB indexes if MongoDB is configured
    try:
        if settings.MONGODB_URI:
            col = get_users_collection()
            await col.create_index("email", unique=True)
            logger.info("✅ Ensured unique index on users.email")
    except Exception as e:
        logger.warning(f"⚠️ Skipped MongoDB index creation: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event for cleanup"""
    logger.info("👋 Shutting down Catalyst Career AI...")

# Health check endpoint (additional to the one in chat router)
@app.get("/ping")
async def ping():
    """Simple ping endpoint for basic health check"""
    return {"status": "alive", "message": "pong"}

# API status endpoint
@app.get("/api/status")
async def api_status():
    """Get detailed API status information"""
    try:
        return {
            "status": "operational",
            "services": {
                "rag_system": "operational",
                "crew_ai": "operational",
                "vector_database": "operational"
            },
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "model": settings.GEMINI_MODEL
        }
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "version": "1.0.0"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )
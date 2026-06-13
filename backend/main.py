import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.services.config import is_groq_configured
from backend.api.router import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s (%(threadName)s): %(message)s'
)
logger = logging.getLogger("BRDGenie")

# Initialize database schema
try:
    init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error(f"Database initialization failed: {type(e).__name__} - {str(e)}")

# Initialize FastAPI App
app = FastAPI(
    title="BRD Genie Backend API",
    description="Refactored, production-ready, observable multi-agent backend using LangGraph, CrewAI, Groq and Sarvam.",
    version="1.0.0"
)

# Apply Security Headers Middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/api/health")
def health():
    agents_ready = is_groq_configured()
    return {
        "status": "ok",
        "agents_ready": agents_ready,
        "message": "BRD Genie backend API is running." if agents_ready else "Running in fallback mode (GROQ_API_KEY is not configured)."
    }

# Mount modularized routes
app.include_router(api_router, prefix="/api")

logger.info("BRD Genie Backend API started successfully.")

"""
Grievance360 - AICTE AI-Powered Grievance Redressal Platform
FastAPI Application Entry Point with SentenceTransformer NLP Routing and Dynamic SLA Engine.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add apps/api directory to sys.path so router/service imports resolve consistently
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routers import complaints, health, analytics, multilingual, whatsapp_bot, telegram_bot, chatbot
from services.nlp_engine import NLPEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler:
    Initializes sentence-transformers embeddings model and pre-computes bureau vectors.
    """
    print("[Grievance360 API] Initializing application services...")
    # Trigger lazy load of singleton NLP engine at startup
    NLPEngine.get_instance()
    print("[Grievance360 API] NLP Engine and Bureau vectors ready.")
    yield
    print("[Grievance360 API] Service shutdown complete.")


app = FastAPI(
    title="Grievance360 API",
    version="1.0.0",
    description=(
        "Centralized AICTE Grievance Redressal and Analytics Platform. "
        "Features automated sentence-transformers semantic triage, dynamic SLA assignment, "
        "PostGIS geospatial routing, duplicate detection, and tamper-evident audit logs."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-Origin Resource Sharing (CORS) Configuration
# Enabled for Next.js frontend running on localhost, Vercel preview URLs, and custom production domains
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://grievance360.vercel.app",
    "https://grievance-360.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz", tags=["Health"])
async def healthz():
    """
    Lightweight zero-dependency healthcheck for Render and Cloud Load Balancers.
    """
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# Register Sub-Routers
app.include_router(health.router)
app.include_router(complaints.router)
app.include_router(analytics.router)
app.include_router(multilingual.router)
app.include_router(whatsapp_bot.router)
app.include_router(telegram_bot.router)
app.include_router(chatbot.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root discovery endpoint providing service health and documentation links.
    """
    return {
        "service": "Grievance360 AICTE Grievance Redressal Engine",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "register_complaint": "POST /api/v1/complaints/register",
            "track_complaint": "GET /api/v1/complaints/track/{complaint_id}",
            "list_complaints": "GET /api/v1/complaints/",
            "health_probe": "GET /api/v1/health/",
            "whatsapp_bot": "POST /api/v1/bot/whatsapp",
            "telegram_bot": "POST /api/v1/bot/telegram",
            "in_app_chatbot": "POST /api/v1/bot/chat",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

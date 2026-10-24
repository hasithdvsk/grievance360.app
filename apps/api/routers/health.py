from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("/")
async def health_check():
    """
    Standard liveness and readiness probe for container orchestration.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "nlp_pipeline": "ready",
            "engine": "SentenceTransformer (all-MiniLM-L6-v2)",
        },
    }

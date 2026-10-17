from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.core.redis import idempotency_cache

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", status_code=status.HTTP_200_OK, summary="Service Health & Diagnostics")
async def check_health(db: AsyncSession = Depends(get_db)):
    """
    Checks operational health of FastAPI application, PostgreSQL database, and Redis cache.
    """
    db_status = "unhealthy"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    redis_status = "connected" if idempotency_cache._is_redis_available else "in_memory_fallback"

    overall_status = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "app_name": settings.app.name,
        "version": settings.app.version,
        "environment": settings.app.env,
        "components": {
            "database": db_status,
            "redis_cache": redis_status,
            "meta_cloud_api": "configured"
        }
    }

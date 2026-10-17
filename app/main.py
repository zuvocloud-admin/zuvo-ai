from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import init_db
from app.core.redis import idempotency_cache
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan managing startup and shutdown tasks cleanly.
    """
    # 1. Initialize logging
    setup_logging()
    logger.info(f"Starting {settings.app.name} v{settings.app.version} in {settings.app.env} mode.")

    # 2. Initialize Database Schema
    await init_db()

    # 3. Connect Redis / Idempotency Cache
    await idempotency_cache.connect()

    yield

    # Shutdown
    logger.info("Shutting down ZuvoCloud application.")
    await idempotency_cache.disconnect()


def create_application() -> FastAPI:
    """Factory function for FastAPI application."""
    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        description="Multi-Tenant WhatsApp AI Operations Platform - Ingestion & Attribution Engine",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.app.api_prefix)

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )

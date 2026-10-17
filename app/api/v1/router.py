from fastapi import APIRouter
from app.api.v1.webhook import router as webhook_router
from app.api.v1.messages import router as messages_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(webhook_router)
api_v1_router.include_router(messages_router)
api_v1_router.include_router(dashboard_router)

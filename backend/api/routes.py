"""
API routes - aggregates all route modules
"""
from fastapi import APIRouter
from .endpoints import chat, debug, health

router = APIRouter()

# Include route modules
router.include_router(health.router)
router.include_router(chat.router)
router.include_router(debug.router)

__all__ = ["router"]

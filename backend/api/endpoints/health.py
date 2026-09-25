"""Health check routes (SupportPilot AI)."""
from fastapi import APIRouter
from ...schemas import HealthResponse, SystemInfoResponse
import os

router = APIRouter(prefix="", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="SupportPilot AI is running",
    )


@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info():
    """Get system information."""
    return SystemInfoResponse(
        name="SupportPilot AI (Personal Edition)",
        version="2.0.0-personal",
        llm_model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        database="SQLite (default) or PostgreSQL",
    )

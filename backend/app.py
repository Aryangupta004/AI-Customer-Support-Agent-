"""SupportPilot AI - FastAPI app factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import init_db
from .api import router


def create_app() -> FastAPI:
    """
    Create and configure the SupportPilot FastAPI application.
    """
    app = FastAPI(
        title="SupportPilot AI",
        description="Personal AI help-desk assistant (RAG + ticket lookup)",
        version="2.0.0-personal",
    )

    # Try to initialize the database, but don't crash the import —
    # the startup event below retries and logs a friendly message.
    try:
        init_db()
    except Exception as e:
        print(f"Note: initial DB setup deferred ({e})")

    # ==================== Middleware ====================

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==================== Startup/Shutdown Events ====================

    @app.on_event("startup")
    async def startup_event():
        """Initialize database on startup"""
        try:
            init_db()
            print("SupportPilot database ready")
        except Exception as e:
            print(f"SupportPilot DB needs manual setup: {e}")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        print("SupportPilot shutting down")

    # ==================== Routes ====================

    app.include_router(router)

    # ==================== Root Endpoint ====================

    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "SupportPilot AI API",
            "version": "2.0.0-personal",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    return app


# Create app instance for ASGI server
app = create_app()

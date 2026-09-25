"""
SupportPilot AI — FastAPI entry point.
"""
import os
import uvicorn
from dotenv import load_dotenv
from .app import create_app

load_dotenv()

# Create the FastAPI application
app = create_app()


if __name__ == "__main__":
    """
    Run the FastAPI application

    Environment variables:
        - API_HOST: Server host (default: 127.0.0.1)
        - API_PORT: Server port (default: 8000)
    """
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))

    print("Starting SupportPilot AI")
    print(f"Server: http://{host}:{port}")
    print(f"Docs: http://{host}:{port}/docs")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
    )

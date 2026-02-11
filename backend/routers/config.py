"""
Configuration endpoint for frontend
"""
import os
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config")
async def get_config():
    """
    Return frontend configuration.
    This endpoint provides runtime configuration to the frontend.
    """
    return {
        "API_BASE_URL": os.environ.get("VITE_API_BASE_URL", "http://127.0.0.1:8000")
    }
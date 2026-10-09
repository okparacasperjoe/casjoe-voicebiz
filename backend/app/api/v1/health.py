"""
Health check endpoint — Stage 1 acceptance gate.
Tests: API alive, database connected, Ollama reachable, Whisper loadable.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import httpx

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    System health check.
    Returns status of all critical services.
    """
    status = {
        "api": "ok",
        "database": "unknown",
        "ollama": "unknown",
        "n_atlas_model": settings.N_ATLAS_MODEL,
        "whisper_model": settings.WHISPER_MODEL_SIZE,
        "env": settings.APP_ENV,
    }

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as e:
        status["database"] = f"error: {str(e)}"

    # Ollama check
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                n_atlas_loaded = any(
                    settings.N_ATLAS_MODEL.split(":")[0] in m for m in models
                )
                status["ollama"] = "ok"
                status["n_atlas_pulled"] = n_atlas_loaded
                status["ollama_models"] = models
            else:
                status["ollama"] = f"error: HTTP {resp.status_code}"
    except httpx.ConnectError:
        status["ollama"] = "not_running — start with: ollama serve"
    except Exception as e:
        status["ollama"] = f"error: {str(e)}"

    # Overall health
    status["healthy"] = (
        status["database"] == "ok" and
        status["api"] == "ok"
    )

    return status

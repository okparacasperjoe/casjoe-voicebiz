"""
Casjoe VoiceBiz — FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import health, transcribe, intent, query, financial_literacy, evaluation, crm

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("VoiceBiz starting up...")
    await init_db()
    logger.info(f"N-ATLAS model: {settings.N_ATLAS_MODEL}")
    logger.info(f"Whisper model: {settings.WHISPER_MODEL_SIZE}")
    yield
    logger.info("VoiceBiz shutting down.")


app = FastAPI(
    title="Casjoe VoiceBiz API",
    description="Voice-first business assistant for Nigerian SMEs — NAIC 2026",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.APP_ENV == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
os.makedirs("public/audio", exist_ok=True)
app.mount("/audio", StaticFiles(directory="public/audio"), name="audio")

# Register routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(transcribe.router, prefix="/api/v1", tags=["asr"])
app.include_router(intent.router, prefix="/api/v1", tags=["intent"])
app.include_router(query.router, prefix="/api/v1", tags=["business-data"])
app.include_router(financial_literacy.router, prefix="/api/v1", tags=["financial-literacy"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["evaluation"])
app.include_router(crm.router, prefix="/api/v1", tags=["crm"])

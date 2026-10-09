"""
Standalone intent classification endpoint — Stage 3 proof.
"""
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel

from app.core.auth import get_current_user, TokenPayload
from app.services.natlas import classify_intent

router = APIRouter()
logger = logging.getLogger(__name__)


class IntentResponse(BaseModel):
    intent: str
    mode: str
    confidence: float
    entities: dict
    language: str
    processing_ms: int


@router.post("/intent", response_model=IntentResponse)
async def get_intent(
    transcript: str = Form(...),
    language: str = Form(default="eng"),
    current_user: TokenPayload = Depends(get_current_user),
):
    """
    Classify the intent of a text transcript using N-ATLAS.
    """
    try:
        intent_result, _, _, latency_ms = await classify_intent(transcript, language)
        return IntentResponse(
            intent=intent_result.get("intent", "AMBIGUOUS"),
            mode=intent_result.get("mode", "ambiguous"),
            confidence=intent_result.get("confidence", 0.0),
            entities=intent_result.get("entities", {}),
            language=language,
            processing_ms=latency_ms,
        )
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

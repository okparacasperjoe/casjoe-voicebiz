"""
Transcription endpoint — Stage 2.
Accepts audio upload, returns ASR transcript.
"""
import os
import uuid
import asyncio
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from app.core.auth import get_current_user, TokenPayload
from app.core.config import settings
from app.services.asr import transcribe_audio, convert_to_wav

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.AUDIO_UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class TranscriptResponse(BaseModel):
    transcript: str
    detected_language: str
    detected_language_probability: float
    duration_seconds: float
    processing_ms: int
    audio_file_ref: str


@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe(
    audio: UploadFile = File(..., description="Audio file — WAV, WebM, MP3, OGG"),
    language: str = Form(default="eng", description="Language hint: eng|ibo|yor|hau"),
    current_user: TokenPayload = Depends(get_current_user),
):
    """
    Stage 2 core endpoint.
    Accepts audio, runs faster-whisper ASR, returns transcript.
    The audio_file_ref can be stored in the interaction log for NAIC evidence.
    """
    if language not in ("eng", "ibo", "yor", "hau"):
        language = "eng"

    # Save uploaded audio
    session_id = str(uuid.uuid4())
    raw_filename = f"{session_id}_raw{Path(audio.filename or 'audio.webm').suffix}"
    raw_path = UPLOAD_DIR / raw_filename
    wav_path = UPLOAD_DIR / f"{session_id}.wav"

    try:
        content = await audio.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        max_size = settings.MAX_AUDIO_DURATION_SECONDS * 32000  # rough upper bound
        if len(content) > max_size * 4:
            raise HTTPException(status_code=413, detail="Audio file too large")

        raw_path.write_bytes(content)

        # Convert to 16kHz WAV for Whisper
        await run_in_threadpool(convert_to_wav, str(raw_path), str(wav_path))

        # Transcribe
        result = await run_in_threadpool(transcribe_audio, str(wav_path), language)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Clean up raw file; keep WAV for logging reference
        if raw_path.exists():
            raw_path.unlink()

    audio_file_ref = f"uploads/{session_id}.wav"

    return TranscriptResponse(
        transcript=result["transcript"],
        detected_language=result["detected_language"],
        detected_language_probability=result["detected_language_probability"],
        duration_seconds=result["duration_seconds"],
        processing_ms=result["processing_ms"],
        audio_file_ref=audio_file_ref,
    )

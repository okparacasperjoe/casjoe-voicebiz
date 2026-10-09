"""
ASR Service — faster-whisper audio transcription.
Loaded once at startup. Accepts audio file path, returns transcript dict.
"""
import time
import logging
import os
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel

from app.core.config import settings

logger = logging.getLogger(__name__)

# Language hint mapping: UI code → Whisper language code
LANGUAGE_MAP = {
    "eng": "en",
    "ibo": "ig",
    "yor": "yo",
    "hau": "ha",
}

# Singleton model — loaded once
_whisper_model: Optional[WhisperModel] = None


def get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL_SIZE} "
                    f"({settings.WHISPER_DEVICE}, {settings.WHISPER_COMPUTE_TYPE})")
        _whisper_model = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )
        logger.info("Whisper model loaded.")
    return _whisper_model


def transcribe_audio(audio_path: str, language_hint: Optional[str] = None) -> dict:
    """
    Transcribe an audio file.

    Args:
        audio_path: Path to a WAV or MP3 file (16kHz mono preferred)
        language_hint: VoiceBiz language code (eng|ibo|yor|hau) or None for auto-detect

    Returns:
        {
            transcript, detected_language, detected_language_probability,
            duration_seconds, processing_ms
        }
    """
    start = time.perf_counter()
    model = get_whisper_model()

    # Map VoiceBiz code to Whisper code
    whisper_lang = None
    if language_hint and language_hint in LANGUAGE_MAP:
        whisper_lang = LANGUAGE_MAP[language_hint]

    try:
        segments, info = model.transcribe(
            audio_path,
            language=whisper_lang,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            vad_filter=True,          # Filter out silence
            vad_parameters={"min_silence_duration_ms": 500},
        )
        transcript = " ".join([s.text for s in segments]).strip()

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        raise

    processing_ms = int((time.perf_counter() - start) * 1000)

    return {
        "transcript": transcript,
        "detected_language": info.language,
        "detected_language_probability": round(info.language_probability, 3),
        "duration_seconds": round(info.duration, 2),
        "processing_ms": processing_ms,
    }


def convert_to_wav(input_path: str, output_path: str) -> str:
    """
    Convert any audio format to 16kHz mono WAV for Whisper.
    Uses imageio-ffmpeg bundled binary.
    """
    import subprocess
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    cmd = [
        ffmpeg_path, "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")
    return output_path

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
# Note: Whisper tokenizer does not have a separate 'ig' token.
# Setting 'ibo' to None lets Whisper auto-transcribe without throwing ValueError.
LANGUAGE_MAP = {
    "eng": "en",
    "ibo": None,
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

    SILENCE_HALLUCINATIONS = {
        "thanks for watching", "thanks for watching!", "thank you.", "thank you",
        "thank you very much.", "please subscribe", "subtitles by", "bye.", "bye"
    }

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
        detected_lang = info.language if info else "en"
        detected_prob = round(info.language_probability, 3) if info else 0.0
        duration = round(info.duration, 2) if info else 0.0
    except (ValueError, Exception) as e:
        logger.warning(f"VAD transcribe notice ({e}) — retrying without vad_filter")
        try:
            segments, info = model.transcribe(
                audio_path,
                language=whisper_lang,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                vad_filter=False,
            )
            transcript = " ".join([s.text for s in segments]).strip()
            detected_lang = info.language if info else "en"
            detected_prob = round(info.language_probability, 3) if info else 0.0
            duration = round(info.duration, 2) if info else 0.0
        except Exception as e2:
            logger.error(f"Whisper transcription failed completely: {e2}")
            transcript = ""
            detected_lang = "en"
            detected_prob = 0.0
            duration = 0.0

    # Filter out common silence hallucinations
    if transcript.lower().strip(" .!?,") in SILENCE_HALLUCINATIONS:
        logger.info(f"Filtered silence hallucination: '{transcript}'")
        transcript = ""

    processing_ms = int((time.perf_counter() - start) * 1000)

    return {
        "transcript": transcript,
        "detected_language": detected_lang,
        "detected_language_probability": detected_prob,
        "duration_seconds": duration,
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

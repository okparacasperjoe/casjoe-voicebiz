"""
Main voice query endpoint — the full pipeline in one call.
Voice → ASR → N-ATLAS intent → Casjoe API or FL Engine → N-ATLAS response → logged.
"""
import uuid
import time
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, TokenPayload
from app.core.database import get_db
from app.core.config import settings
from app.services.asr import transcribe_audio, convert_to_wav
from app.services.natlas import classify_intent, format_response
from app.services.casjoe import CasjoeBizClient
from app.services.financial_literacy import handle_educational_query
from app.models import VoiceInteraction, VoiceSession, AuditLog
from app.services.intent_router import route_intent
from app.services.tts import generate_voice_response

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.AUDIO_UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class VoiceQueryResponse(BaseModel):
    interaction_id: str
    transcript: str
    intent: str
    intent_mode: str
    intent_confidence: float
    response_text: str
    language: str
    total_latency_ms: int
    task_success: bool
    clarification_needed: bool = False
    clarification_prompt: str | None = None
    error_code: str | None = None
    audio_url: str | None = None


@router.post("/query", response_model=VoiceQueryResponse)
async def voice_query(
    audio: UploadFile = File(...),
    language: str = Form(default="eng"),
    session_id: str = Form(default=None),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full VoiceBiz pipeline endpoint.
    Accepts audio, returns a complete voice response backed by real business data.
    """
    pipeline_start = time.perf_counter()
    interaction_id = str(uuid.uuid4())
    error_code = None
    task_success = False

    # ── Step 1: Save & convert audio ─────────────────────────────────────────
    raw_path = UPLOAD_DIR / f"{interaction_id}_raw.webm"
    wav_path = UPLOAD_DIR / f"{interaction_id}.wav"

    try:
        content = await audio.read()
        raw_path.write_bytes(content)
        await run_in_threadpool(convert_to_wav, str(raw_path), str(wav_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {e}")
    finally:
        if raw_path.exists():
            raw_path.unlink()

    # ── Step 2: ASR ───────────────────────────────────────────────────────────
    try:
        asr_result = await run_in_threadpool(transcribe_audio, str(wav_path), language)
    except Exception as e:
        error_code = "E1"
        logger.error(f"ASR failed [{interaction_id}]: {e}")
        await _save_interaction(db, interaction_id, current_user, language,
                                str(wav_path), error_code=error_code)
        fallback_msg = _get_fallback_speech_message(language, no_speech=False)
        return VoiceQueryResponse(
            interaction_id=interaction_id,
            transcript="",
            intent="AMBIGUOUS",
            intent_mode="ambiguous",
            intent_confidence=0.0,
            response_text=fallback_msg,
            language=language,
            total_latency_ms=int((time.perf_counter() - pipeline_start) * 1000),
            task_success=False,
            error_code="E1",
        )

    transcript = asr_result["transcript"]
    if not transcript:
        fallback_msg = _get_fallback_speech_message(language, no_speech=True)
        return VoiceQueryResponse(
            interaction_id=interaction_id,
            transcript="",
            intent="AMBIGUOUS",
            intent_mode="ambiguous",
            intent_confidence=0.0,
            response_text=fallback_msg,
            language=language,
            total_latency_ms=int((time.perf_counter() - pipeline_start) * 1000),
            task_success=False,
            error_code="E1",
        )

    # Automatically adapt language to native dialect if recognized in speech
    language = detect_language_from_text(transcript, language)

    # ── Step 3: N-ATLAS intent classification ─────────────────────────────────
    try:
        intent_result, intent_req, intent_raw, intent_ms = await classify_intent(
            transcript, language
        )
    except Exception as e:
        error_code = "E2"
        logger.error(f"Intent classification failed [{interaction_id}]: {e}")
        intent_result = {"intent": "AMBIGUOUS", "mode": "ambiguous", "confidence": 0.0, "entities": {}}
        intent_req, intent_raw, intent_ms = [], "", 0

    intent = intent_result.get("intent", "AMBIGUOUS")
    intent_mode = intent_result.get("mode", "ambiguous")
    confidence = intent_result.get("confidence", 0.0)
    entities = intent_result.get("entities", {})

    # ── Handle ambiguity and out-of-scope ─────────────────────────────────────
    if intent == "AMBIGUOUS":
        clarification = _get_clarification_prompt(transcript, language)
        return VoiceQueryResponse(
            interaction_id=interaction_id,
            transcript=transcript,
            intent=intent,
            intent_mode="ambiguous",
            intent_confidence=confidence,
            response_text=clarification,
            language=language,
            total_latency_ms=int((time.perf_counter() - pipeline_start) * 1000),
            task_success=True,
            clarification_needed=True,
            clarification_prompt=clarification,
            error_code="E6",
        )

    if intent == "OUT_OF_SCOPE":
        return VoiceQueryResponse(
            interaction_id=interaction_id,
            transcript=transcript,
            intent=intent,
            intent_mode="ambiguous",
            intent_confidence=confidence,
            response_text=_get_out_of_scope_message(language),
            language=language,
            total_latency_ms=int((time.perf_counter() - pipeline_start) * 1000),
            task_success=True,
        )

    # ── Step 4: Route to data source ──────────────────────────────────────────
    casjoe_client = CasjoeBizClient(
        jwt_token=_extract_jwt_from_user(current_user),
        business_id=current_user.business_id,
    )

    business_data, api_endpoint, api_status, api_ms = await route_intent(
        intent=intent,
        entities=entities,
        casjoe_client=casjoe_client,
        fl_transcript=transcript,
        fl_language=language,
    )

    if api_status and api_status >= 400:
        error_code = "E3"

    # ── Step 5: N-ATLAS response formatting ───────────────────────────────────
    try:
        response_text, resp_req, resp_ms = await format_response(
            transcript=transcript,
            business_data=business_data,
            language=language,
        )
        task_success = True
    except Exception as e:
        error_code = "E4"
        logger.error(f"Response formatting failed [{interaction_id}]: {e}")
        
        fallback_msgs = {
            "eng": "I found information but had trouble explaining it. Result:",
            "ibo": "Ahụrụ m ozi mana enwere m nsogbu ịkọwa ya. Nsonaazụ:",
            "yor": "Mo ri alaye sugbon mo ni isoro lati se alaye re. Esi:",
            "hau": "Na sami bayani amma na sami matsala bayyana shi. Sakamako:"
        }
        msg = fallback_msgs.get(language, fallback_msgs["eng"])
        response_text = f"{msg} {business_data}"
        resp_req, resp_ms = [], 0
    # ── Step 5.5: Custom Voice Generation (N-ATLaS TTS) ───────────────────────
    try:
        audio_url = await generate_voice_response(response_text, language)
    except Exception as e:
        logger.error(f"TTS generation failed [{interaction_id}]: {e}")
        audio_url = None

    total_ms = int((time.perf_counter() - pipeline_start) * 1000)

    # ── Step 6: Log interaction ───────────────────────────────────────────────
    await _save_interaction(
        db=db,
        interaction_id=interaction_id,
        current_user=current_user,
        language=language,
        audio_file_ref=str(wav_path),
        asr_result=asr_result,
        intent_result=intent_result,
        intent_req=intent_req,
        intent_raw=intent_raw,
        intent_ms=intent_ms,
        api_endpoint=api_endpoint,
        api_status=api_status,
        api_ms=api_ms,
        resp_req=resp_req,
        response_text=response_text,
        resp_ms=resp_ms,
        total_ms=total_ms,
        task_success=task_success,
        error_code=error_code,
    )

    return VoiceQueryResponse(
        interaction_id=interaction_id,
        transcript=transcript,
        intent=intent,
        intent_mode=intent_mode,
        intent_confidence=confidence,
        response_text=response_text,
        language=language,
        total_latency_ms=total_ms,
        task_success=task_success,
        error_code=error_code,
        audio_url=audio_url,
    )


@router.post("/text_query", response_model=VoiceQueryResponse)
async def text_query(
    transcript: str = Form(...),
    language: str = Form(default="eng"),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Text-based query pipeline for simulation and testing.
    Skips ASR and goes straight to intent classification.
    """
    pipeline_start = time.perf_counter()
    interaction_id = str(uuid.uuid4())
    error_code = None
    task_success = False

    # Automatically detect native language if transcript uses regional phrasing
    language = detect_language_from_text(transcript, language)

    # ── Step 3: N-ATLAS intent classification ─────────────────────────────────
    try:
        intent_result, intent_req, intent_raw, intent_ms = await classify_intent(
            transcript, language
        )
    except Exception as e:
        error_code = "E2"
        logger.error(f"Intent classification failed [{interaction_id}]: {e}")
        intent_result = {"intent": "AMBIGUOUS", "mode": "ambiguous", "confidence": 0.0, "entities": {}}
        intent_req, intent_raw, intent_ms = [], "", 0

    intent = intent_result.get("intent", "AMBIGUOUS")
    intent_mode = intent_result.get("mode", "ambiguous")
    confidence = intent_result.get("confidence", 0.0)
    entities = intent_result.get("entities", {})

    # ── Handle ambiguity and out-of-scope ─────────────────────────────────────
    if intent == "AMBIGUOUS":
        clarification = _get_clarification_prompt(transcript, language)
        return VoiceQueryResponse(
            interaction_id=interaction_id,
            transcript=transcript,
            intent=intent,
            intent_mode="ambiguous",
            intent_confidence=confidence,
            response_text=clarification,
            language=language,
            total_latency_ms=int((time.perf_counter() - pipeline_start) * 1000),
            task_success=True,
            clarification_needed=True,
            clarification_prompt=clarification,
            error_code="E6",
        )

    if intent == "OUT_OF_SCOPE":
        return VoiceQueryResponse(
            interaction_id=interaction_id,
            transcript=transcript,
            intent=intent,
            intent_mode="ambiguous",
            intent_confidence=confidence,
            response_text=_get_out_of_scope_message(language),
            language=language,
            total_latency_ms=int((time.perf_counter() - pipeline_start) * 1000),
            task_success=True,
        )

    # ── Step 4: Route to data source ──────────────────────────────────────────
    casjoe_client = CasjoeBizClient(
        jwt_token=_extract_jwt_from_user(current_user),
        business_id=current_user.business_id,
    )

    business_data, api_endpoint, api_status, api_ms = await route_intent(
        intent=intent,
        entities=entities,
        casjoe_client=casjoe_client,
        fl_transcript=transcript,
        fl_language=language,
    )

    if api_status and api_status >= 400:
        error_code = "E3"

    # ── Step 5: N-ATLAS response formatting ───────────────────────────────────
    try:
        response_text, resp_req, resp_ms = await format_response(
            transcript=transcript,
            business_data=business_data,
            language=language,
        )
        task_success = True
    except Exception as e:
        error_code = "E4"
        logger.error(f"Response formatting failed [{interaction_id}]: {e}")
        fallback_msgs = {
            "eng": "I found information but had trouble explaining it. Result:",
            "ibo": "Ahụrụ m ozi mana enwere m nsogbu ịkọwa ya. Nsonaazụ:",
            "yor": "Mo ri alaye sugbon mo ni isoro lati se alaye re. Esi:",
            "hau": "Na sami bayani amma na sami matsala bayyana shi. Sakamako:"
        }
        msg = fallback_msgs.get(language, fallback_msgs["eng"])
        response_text = f"{msg} {business_data}"
        resp_req, resp_ms = [], 0

    # ── Step 5.5: Custom Voice Generation (N-ATLaS TTS) ───────────────────────
    try:
        audio_url = await generate_voice_response(response_text, language)
    except Exception as e:
        logger.error(f"TTS generation failed [{interaction_id}]: {e}")
        audio_url = None

    total_ms = int((time.perf_counter() - pipeline_start) * 1000)

    # ── Step 6: Log interaction ───────────────────────────────────────────────
    await _save_interaction(
        db=db,
        interaction_id=interaction_id,
        current_user=current_user,
        language=language,
        audio_file_ref="text_simulation",
        asr_result=None,
        intent_result=intent_result,
        intent_req=intent_req,
        intent_raw=intent_raw,
        intent_ms=intent_ms,
        api_endpoint=api_endpoint,
        api_status=api_status,
        api_ms=api_ms,
        resp_req=resp_req,
        response_text=response_text,
        resp_ms=resp_ms,
        total_ms=total_ms,
        task_success=task_success,
        error_code=error_code,
    )

    return VoiceQueryResponse(
        interaction_id=interaction_id,
        transcript=transcript,
        intent=intent,
        intent_mode=intent_mode,
        intent_confidence=confidence,
        response_text=response_text,
        language=language,
        total_latency_ms=total_ms,
        task_success=task_success,
        error_code=error_code,
        audio_url=audio_url,
    )


def _get_fallback_speech_message(language: str, no_speech: bool = False) -> str:
    """Return speech recognition fallback messages in the user's native language."""
    messages = {
        "ibo": {
            "unclear": "Anụghị m ihe ị kwuru nke ọma. Biko nwaa ọzọ n'ebe dị nwayọ ma kwuo ya ọzọ.",
            "no_speech": "Anụghị m olu ọ bụla. Biko pịa bọtịnụ ma kwuo okwu ọzọ."
        },
        "yor": {
            "unclear": "Mi ò gbọ́ ohun tí o sọ dáadáa. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i níbi tí kò sí ariwo.",
            "no_speech": "Mi ò gbọ́ ohùn kankan. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i."
        },
        "hau": {
            "unclear": "Ban ji abin da kuka fada da kyau ba. Da fatan za a sake gwadawa a wurin da ba hayaniya.",
            "no_speech": "Ban ji wata magana ba. Da fatan za a sake gwadawa."
        },
        "eng": {
            "unclear": "I didn't catch that clearly. Could you try again in a quieter place?",
            "no_speech": "I didn't catch any speech. Please try again."
        }
    }
    lang_set = messages.get(language, messages["eng"])
    return lang_set["no_speech"] if no_speech else lang_set["unclear"]


def _get_clarification_prompt(transcript: str, language: str) -> str:
    """
    Generate a clarification prompt for ambiguous queries in the requested language.
    """
    lower = transcript.lower()
    is_profit_q = any(w in lower for w in ["make", "earn", "get"])
    
    prompts = {
        "eng": {
            "profit": "Do you mean your total sales revenue, or your profit after expenses?",
            "general": "I'm not sure what you're asking. Could you rephrase? For example: 'How much did I sell this week?' or 'What is profit?'"
        },
        "ibo": {
            "profit": "Ị na-ekwu maka ngụkọta ego ị nwetara na ahịa, ka ọ bụ uru ị nwetara mgbe ị wepụrụ mmefu?",
            "general": "aghọtaghị m ihe ị na-ajụ. Biko ị nwere ike ikwughachi ya? Dị ka atụ: 'Ego ole ka m rere n'izu a?' ma ọ bụ 'Gịnị bụ uru ahịa?'"
        },
        "yor": {
            "profit": "Ṣé o n sọ nípa apapọ owó tí o pa, tàbí èrè lẹ́yìn tí o ti yọ owó ináwó?",
            "general": "Mi o mọ ohun tí o n beere. Ṣé o le tún un sọ? Fún àpẹrẹ: 'Elo ni mo ta ní ọ̀sẹ̀ yìí?' tàbí 'Kí ni èrè?'"
        },
        "hau": {
            "profit": "Kuna nufin jimillar kudin da kuka samu na sayarwa ne, ko ribar ku bayan fitar da kashe kudi?",
            "general": "Ban gane abin da kuke tambaya ba. Za ku iya sake fadawa? Misali: 'Nawa na sayar a wannan satin?' ko 'Menene riba?'"
        }
    }
    
    lang_prompts = prompts.get(language, prompts["eng"])
    return lang_prompts["profit"] if is_profit_q else lang_prompts["general"]


def detect_language_from_text(transcript: str, current_language: str) -> str:
    """
    Auto-detect whether transcript contains distinctive Igbo, Yoruba, or Hausa markers.
    If detected, prioritize that native language so responses and speech match.
    """
    if not transcript:
        return current_language

    text = transcript.lower().strip()
    words = set(text.replace("?", " ").replace("!", " ").replace(".", " ").replace(",", " ").split())

    # Igbo markers
    igbo_markers = {
        "ego", "ole", "kedu", "ahia", "ahịa", "rere", "anyi", "anyị",
        "taa", "ugwo", "ụgwọ", "onye", "ndị", "ndi", "uru", "mmefu",
        "ndụmọdụ", "ndumodu", "gịnị", "gini", "bụ", "bu", "biko",
        "nwetara", "azụmahịa", "azumahia", "ngwaahịa", "ngwaahia",
        "dalu", "dalụ", "ụtụtụ", "ututu", "ọma", "oma"
    }

    # Yoruba markers
    yoruba_markers = {
        "bawo", "elo", "kini", "owo", "ere", "gbese", "inawọ", "inawo",
        "onibara", "ọjọ", "ojo", "loni", "imoran", "imọran", "tani", "se"
    }

    # Hausa markers
    hausa_markers = {
        "nawa", "yaya", "riba", "bashi", "sayar", "kudi", "kuɗi", "yau",
        "kasuwanci", "shawara", "kudin", "menene", "wanene", "sannu"
    }

    if any(m in words for m in igbo_markers) or any(p in text for p in ["ego ole", "onye ji", "ndị ji", "ndi ji", "ahia taa", "ahịa taa", "ndụmọdụ", "ndumodu"]):
        return "ibo"
    if any(m in words for m in yoruba_markers) or any(p in text for p in ["elo ni", "tani o", "kini ere", "imoran owo"]):
        return "yor"
    if any(m in words for m in hausa_markers) or any(p in text for p in ["nawa na", "kudin shiga", "shawarar kudi"]):
        return "hau"

    return current_language


def _get_out_of_scope_message(language: str) -> str:
    """Return an out-of-scope response strictly in the target language."""
    messages = {
        "ibo": (
            "Enwere m ike inyere gị aka naanị maka ajụjụ gbasara azụmahịa gị — "
            "ahịa gị, ego mmefu, ndị ji gị ụgwọ, ma ọ bụ ndụmọdụ ego azụmahịa. "
            "Kedu ihe ị ga-achọ ịma?"
        ),
        "yor": (
            "Mo le ran ọ lọwọ pẹlu awọn ibeere nipa iṣowo rẹ nikan — "
            "awọn tita rẹ, inawo, awọn onibara ti o jẹ ọ ni gbese, tabi imọran owo. "
            "Kini iwọ yoo fẹ lati mọ?"
        ),
        "hau": (
            "Zan iya taimaka muku ne kawai da tambayoyi game da kasuwancin ku — "
            "tallace-tallacen ku, kashe kuɗi, abokan cinikin ku, ko shawarar kudi. "
            "Menene kuke so ku sani?"
        ),
        "eng": (
            "I can only help with questions about your business — "
            "your sales, expenses, customers, or financial literacy. "
            "What would you like to know?"
        ),
    }
    return messages.get(language, messages["eng"])


def _extract_jwt_from_user(user: TokenPayload) -> str:
    """Placeholder — in production, extract from request context."""
    return ""


async def _save_interaction(db, interaction_id, current_user, language, audio_file_ref,
                             asr_result=None, intent_result=None, intent_req=None,
                             intent_raw=None, intent_ms=None, api_endpoint=None,
                             api_status=None, api_ms=None, resp_req=None,
                             response_text=None, resp_ms=None, total_ms=None,
                             task_success=None, error_code=None):
    """Persist the full interaction to the database for NAIC evidence."""
    try:
        interaction = VoiceInteraction(
            id=interaction_id,
            user_id=current_user.user_id,
            business_id=current_user.business_id,
            language_hint=language,
            audio_file_ref=audio_file_ref,
            asr_transcript=asr_result.get("transcript") if asr_result else None,
            asr_detected_language=asr_result.get("detected_language") if asr_result else None,
            asr_confidence=asr_result.get("detected_language_probability") if asr_result else None,
            asr_duration_ms=int((asr_result.get("duration_seconds", 0) or 0) * 1000) if asr_result else None,
            asr_processing_ms=asr_result.get("processing_ms") if asr_result else None,
            n_atlas_intent_request=intent_req,
            n_atlas_intent_response_raw=intent_raw,
            intent=intent_result.get("intent") if intent_result else None,
            intent_mode=intent_result.get("mode") if intent_result else None,
            intent_confidence=intent_result.get("confidence") if intent_result else None,
            entities=intent_result.get("entities") if intent_result else None,
            n_atlas_intent_ms=intent_ms,
            casjoe_api_endpoint=api_endpoint,
            casjoe_api_status=api_status,
            casjoe_api_ms=api_ms,
            n_atlas_response_request=resp_req,
            response_text=response_text,
            n_atlas_response_ms=resp_ms,
            total_latency_ms=total_ms,
            task_success=task_success,
            error_code=error_code,
        )
        db.add(interaction)
        await db.flush()
    except Exception as e:
        logger.error(f"Failed to save interaction to DB: {e}")

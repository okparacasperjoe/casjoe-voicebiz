"""
N-ATLAS service — intent classification and response generation via Ollama.
This is the core AI integration. Every call is logged for NAIC evidence.
"""
import json
import time
import logging
import httpx
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Prompts ──────────────────────────────────────────────────────────────────

INTENT_SYSTEM_PROMPT = """You are a business assistant helping Nigerian SME owners understand their business data. Your task is to classify the user's question.

Given a user message in English, Igbo, Yoruba, or Hausa, return ONLY a JSON object with no explanation:
{
  "intent": "<INTENT_ID>",
  "entities": {
    "period": "<today|week|month|null>",
    "customer_name": "<string or null>",
    "amount": "<number or null>",
    "product_name": "<string or null>"
  },
  "confidence": <0.0 to 1.0>,
  "language": "<eng|ibo|yor|hau>",
  "mode": "<data|educational|action|ambiguous>"
}

Approved INTENT_IDs:
FINANCIAL_ADVICE, SALES_TODAY, SALES_WEEK, SALES_MONTH, SALES_TREND, TOP_PRODUCTS,
CUSTOMER_BALANCES, CUSTOMER_DETAILS, TOP_CUSTOMERS,
EXPENSES_TODAY, EXPENSES_MONTH, TOP_EXPENSES,
INVENTORY_STATUS, LOW_STOCK, INVENTORY_VALUE, BUSINESS_SUMMARY,
FL_REVENUE_PROFIT, FL_WHAT_IS_PROFIT, FL_CASH_FLOW, FL_SEPARATE_MONEY,
FL_BUDGETING, FL_EXPENSE_TRACKING, FL_CREDIT_MGMT, FL_PRICING, FL_SAVINGS, FL_INVOICES,
ACTION_CREATE_INVOICE, ACTION_RECORD_EXPENSE, ACTION_RECORD_PAYMENT,
AMBIGUOUS, OUT_OF_SCOPE, GREETING

Return only the JSON object."""

RESPONSE_SYSTEM_PROMPT_TEMPLATE = """You are VoiceBiz, an elite voice-first financial expert and business intelligence advisor for business owners. You speak in a confident, sharp, warm, and highly practical manner.

Rules:
1. Act as a trusted Chief Financial Officer (CFO) and financial expert. Don't just echo back numbers—interpret what the numbers mean for the health of their business.
2. If there are high receivables or debts, warn them proactively about cash flow danger: explain that money in debtors' hands is not profit until collected.
3. Use simple, clear, relatable business examples that any merchant understands.
4. Always ground your advice in the exact numbers provided in the data.
5. Provide a clear, actionable next step (e.g. "Collect your overdue balance before buying new stock", "Set aside 15% for inventory re-orders").
6. Keep spoken responses punchy, direct, and under 3-4 sentences so it is pleasant to listen to.
7. Respond in {language}.

User question: {transcript}
Business data: {business_data}"""


# ─── Core API call ────────────────────────────────────────────────────────────

async def call_n_atlas(
    messages: list[dict],
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> tuple[str, int]:
    """
    Call N-ATLAS via Ollama local API.
    Returns (response_text, latency_ms).
    Falls back to HuggingFace endpoint if NATLAS_ENDPOINT is configured.
    """
    start = time.perf_counter()

    # Primary: Ollama local
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": settings.N_ATLAS_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "num_ctx": 2048,
                    },
                },
            )
            resp.raise_for_status()
            text = resp.json()["message"]["content"].strip()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return text, latency_ms

    except httpx.ConnectError:
        logger.warning("Ollama not reachable — trying HF endpoint fallback")

    # Fallback: HuggingFace hosted endpoint (demo/ZeroGPU)
    if settings.NATLAS_ENDPOINT:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                headers = {"Content-Type": "application/json"}
                if settings.HF_TOKEN:
                    headers["Authorization"] = f"Bearer {settings.HF_TOKEN}"
                resp = await client.post(
                    settings.NATLAS_ENDPOINT,
                    headers=headers,
                    json={
                        "inputs": messages,
                        "parameters": {
                            "temperature": temperature,
                            "max_new_tokens": max_tokens,
                        },
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                text = (data.get("generated_text") or "").strip()
                latency_ms = int((time.perf_counter() - start) * 1000)
                return text, latency_ms
        except Exception as e:
            logger.error(f"HF endpoint also failed: {e}")

    raise RuntimeError("N-ATLAS unavailable: Ollama not running and no HF endpoint configured")


# ─── Intent classification ────────────────────────────────────────────────────

async def classify_intent(
    transcript: str,
    language: str = "eng",
) -> tuple[dict, list[dict], str, int]:
    """
    Classify the intent of a transcript using N-ATLAS.

    Returns:
        (parsed_intent_dict, messages_sent, raw_response, latency_ms)
    """
    cleaned_lower = transcript.lower().strip()

    # Fast, deterministic Financial Advisory detection
    if any(k in cleaned_lower for k in [
        "advice", "advise", "financial advice", "financial counsel", "recommendation",
        "gave me financial advice", "give me financial advice", "business advice",
        "what should i do", "how is my business", "cfo", "ndụmọdụ ego", "imọran owo", "shawarar kudi"
    ]):
        result = {
            "intent": "FINANCIAL_ADVICE",
            "entities": {"period": "today"},
            "confidence": 0.98,
            "language": language,
            "mode": "data",
        }
        return result, [], json.dumps(result), 5

    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Language: {language}\nMessage: {transcript}"},
    ]

    raw, latency_ms = await call_n_atlas(messages, temperature=0.1, max_tokens=256)

    # Parse JSON response
    try:
        # Strip markdown code fences if model wraps in ```json ... ```
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:-1])
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(f"Intent JSON parse failed. Raw: {raw[:200]}")
        result = {
            "intent": "AMBIGUOUS",
            "entities": {},
            "confidence": 0.0,
            "language": language,
            "mode": "ambiguous",
        }

    return result, messages, raw, latency_ms


# ─── Response generation ──────────────────────────────────────────────────────

async def format_response(
    transcript: str,
    business_data: dict,
    language: str = "eng",
) -> tuple[str, list[dict], int]:
    """
    Format a plain-language response using N-ATLAS.
    business_data is the verified data from Casjoe Biz (or FL Engine).

    Returns:
        (response_text, messages_sent, latency_ms)
    """
    lang_names = {"eng": "Nigerian English", "ibo": "Igbo", "yor": "Yoruba", "hau": "Hausa"}
    lang_name = lang_names.get(language, "Nigerian English")

    system_prompt = RESPONSE_SYSTEM_PROMPT_TEMPLATE.format(
        language=lang_name,
        transcript=transcript,
        business_data=json.dumps(business_data, ensure_ascii=False, indent=2),
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcript},
    ]

    response_text, latency_ms = await call_n_atlas(messages, temperature=0.3, max_tokens=256)
    return response_text, messages, latency_ms

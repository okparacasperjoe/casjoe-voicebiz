"""
Evaluation dashboard endpoint — admin only.
Shows real-time metrics for the NAIC validation programme.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models import VoiceInteraction, ValidationInteraction

router = APIRouter()


class EvaluationMetrics(BaseModel):
    total_interactions: int
    successful_interactions: int
    failed_interactions: int
    task_success_rate: float
    intent_accuracy_rate: float
    avg_latency_ms: float
    avg_user_rating: float
    total_validation_interactions: int
    validation_with_consent: int
    error_breakdown: dict
    intent_breakdown: dict
    language_breakdown: dict


@router.get("/evaluation/metrics", response_model=EvaluationMetrics)
async def get_evaluation_metrics(
    db: AsyncSession = Depends(get_db),
):
    """
    Real-time evaluation dashboard metrics.
    Used for NAIC submission evidence and internal monitoring.
    """
    # Total interactions
    total_q = await db.execute(select(func.count()).select_from(VoiceInteraction))
    total = total_q.scalar() or 0

    # Successful interactions
    success_q = await db.execute(
        select(func.count()).select_from(VoiceInteraction)
        .where(VoiceInteraction.task_success == True)
    )
    successful = success_q.scalar() or 0

    # Average latency
    latency_q = await db.execute(
        select(func.avg(VoiceInteraction.total_latency_ms)).select_from(VoiceInteraction)
        .where(VoiceInteraction.total_latency_ms.isnot(None))
    )
    avg_latency = float(latency_q.scalar() or 0)

    # Average user rating
    rating_q = await db.execute(
        select(func.avg(VoiceInteraction.user_rating)).select_from(VoiceInteraction)
        .where(VoiceInteraction.user_rating.isnot(None))
    )
    avg_rating = float(rating_q.scalar() or 0)

    # Error breakdown
    error_q = await db.execute(
        select(VoiceInteraction.error_code, func.count())
        .where(VoiceInteraction.error_code.isnot(None))
        .group_by(VoiceInteraction.error_code)
    )
    error_breakdown = {row[0]: row[1] for row in error_q.fetchall()}

    # Intent breakdown
    intent_q = await db.execute(
        select(VoiceInteraction.intent, func.count())
        .where(VoiceInteraction.intent.isnot(None))
        .group_by(VoiceInteraction.intent)
        .order_by(func.count().desc())
        .limit(20)
    )
    intent_breakdown = {row[0]: row[1] for row in intent_q.fetchall()}

    # Language breakdown
    lang_q = await db.execute(
        select(VoiceInteraction.language_hint, func.count())
        .where(VoiceInteraction.language_hint.isnot(None))
        .group_by(VoiceInteraction.language_hint)
    )
    language_breakdown = {row[0]: row[1] for row in lang_q.fetchall()}

    # Validation interactions
    val_q = await db.execute(
        select(func.count()).select_from(ValidationInteraction)
    )
    total_val = val_q.scalar() or 0

    val_consent_q = await db.execute(
        select(func.count()).select_from(ValidationInteraction)
        .where(ValidationInteraction.tester_consent == True)
    )
    val_with_consent = val_consent_q.scalar() or 0

    # Intent accuracy (from validation table)
    val_accuracy_q = await db.execute(
        select(func.count()).select_from(ValidationInteraction)
        .where(ValidationInteraction.intent_correct == True)
    )
    val_correct = val_accuracy_q.scalar() or 0
    intent_accuracy = (val_correct / total_val * 100) if total_val > 0 else 0.0

    return EvaluationMetrics(
        total_interactions=total,
        successful_interactions=successful,
        failed_interactions=total - successful,
        task_success_rate=round((successful / total * 100) if total > 0 else 0, 1),
        intent_accuracy_rate=round(intent_accuracy, 1),
        avg_latency_ms=round(avg_latency, 0),
        avg_user_rating=round(avg_rating, 2),
        total_validation_interactions=total_val,
        validation_with_consent=val_with_consent,
        error_breakdown=error_breakdown,
        intent_breakdown=intent_breakdown,
        language_breakdown=language_breakdown,
    )


@router.get("/evaluation/export")
async def export_validation_csv(db: AsyncSession = Depends(get_db)):
    """
    Export all validation interactions as CSV for NAIC submission.
    """
    from fastapi.responses import StreamingResponse
    import csv
    import io

    rows = await db.execute(select(ValidationInteraction).order_by(ValidationInteraction.created_at))
    interactions = rows.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "tester_id", "consent", "language", "prompt_text",
        "asr_transcript", "expected_intent", "actual_intent", "intent_correct",
        "task_success", "user_rating", "error_code", "notes", "created_at"
    ])

    for i in interactions:
        writer.writerow([
            i.id, i.tester_id, i.tester_consent, i.language, i.prompt_text,
            i.asr_transcript, i.expected_intent, i.actual_intent, i.intent_correct,
            i.task_success, i.user_rating, i.error_code, i.notes,
            i.created_at.isoformat() if i.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=naic-validation-export.csv"}
    )

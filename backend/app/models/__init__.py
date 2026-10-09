"""
SQLAlchemy ORM models — maps to the PRD PostgreSQL schema.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, Float, Text,
    DateTime, ForeignKey, BigInteger, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


def new_uuid():
    return str(uuid.uuid4())


class VoicebizUser(Base):
    __tablename__ = "voicebiz_users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    casjoe_user_id = Column(String(255), unique=True, nullable=False)
    business_id = Column(UUID(as_uuid=False), nullable=False)
    language_preference = Column(String(3), default="eng")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_active_at = Column(DateTime(timezone=True), nullable=True)

    sessions = relationship("VoiceSession", back_populates="user")


class VoiceSession(Base):
    __tablename__ = "voice_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("voicebiz_users.id"))
    business_id = Column(UUID(as_uuid=False), nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    interaction_count = Column(Integer, default=0)
    language = Column(String(3), nullable=True)

    user = relationship("VoicebizUser", back_populates="sessions")
    interactions = relationship("VoiceInteraction", back_populates="session")


class VoiceInteraction(Base):
    __tablename__ = "voice_interactions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("voice_sessions.id"))
    user_id = Column(UUID(as_uuid=False), nullable=False)
    business_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # ASR layer
    audio_file_ref = Column(String(500), nullable=True)
    language_hint = Column(String(3), nullable=True)
    asr_transcript = Column(Text, nullable=True)
    asr_detected_language = Column(String(3), nullable=True)
    asr_confidence = Column(Float, nullable=True)
    asr_duration_ms = Column(Integer, nullable=True)
    asr_processing_ms = Column(Integer, nullable=True)

    # N-ATLAS intent classification
    n_atlas_intent_request = Column(JSON, nullable=True)
    n_atlas_intent_response_raw = Column(Text, nullable=True)
    intent = Column(String(50), nullable=True, index=True)
    intent_mode = Column(String(20), nullable=True)  # data|educational|action|ambiguous
    intent_confidence = Column(Float, nullable=True)
    entities = Column(JSON, nullable=True)
    n_atlas_intent_ms = Column(Integer, nullable=True)

    # Casjoe Biz API
    casjoe_api_endpoint = Column(String(200), nullable=True)
    casjoe_api_response = Column(JSON, nullable=True)
    casjoe_api_status = Column(Integer, nullable=True)
    casjoe_api_ms = Column(Integer, nullable=True)

    # N-ATLAS response
    n_atlas_response_request = Column(JSON, nullable=True)
    response_text = Column(Text, nullable=True)
    n_atlas_response_ms = Column(Integer, nullable=True)

    # Outcome
    total_latency_ms = Column(Integer, nullable=True)
    task_success = Column(Boolean, nullable=True)
    error_code = Column(String(10), nullable=True)
    error_detail = Column(Text, nullable=True)

    # User feedback
    user_rating = Column(Integer, nullable=True)
    user_flagged = Column(Boolean, default=False)

    session = relationship("VoiceSession", back_populates="interactions")


class ValidationInteraction(Base):
    """NAIC evidence table — real user test interactions."""
    __tablename__ = "validation_interactions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tester_id = Column(String(100), nullable=True)
    tester_consent = Column(Boolean, nullable=False, default=False)
    language = Column(String(3), nullable=True)
    prompt_text = Column(Text, nullable=True)
    audio_file_ref = Column(String(500), nullable=True)
    asr_transcript = Column(Text, nullable=True)
    expected_intent = Column(String(50), nullable=True)
    actual_intent = Column(String(50), nullable=True)
    intent_correct = Column(Boolean, nullable=True)
    expected_answer_summary = Column(Text, nullable=True)
    actual_answer = Column(Text, nullable=True)
    task_success = Column(Boolean, nullable=True)
    user_rating = Column(Integer, nullable=True)
    error_code = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)
    evaluator_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class VoiceAction(Base):
    """Write operations triggered via voice (Level 3 safety)."""
    __tablename__ = "voice_actions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    interaction_id = Column(UUID(as_uuid=False), ForeignKey("voice_interactions.id"))
    user_id = Column(UUID(as_uuid=False), nullable=False)
    business_id = Column(UUID(as_uuid=False), nullable=False)
    action_intent = Column(String(50), nullable=True)
    action_payload = Column(JSON, nullable=True)
    confirmation_required = Column(Boolean, default=True)
    confirmed = Column(Boolean, nullable=True)
    executed = Column(Boolean, default=False)
    casjoe_result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AuditLog(Base):
    """Immutable audit trail — append only."""
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    user_id = Column(UUID(as_uuid=False), nullable=True)
    business_id = Column(UUID(as_uuid=False), nullable=True)
    event_type = Column(String(100), nullable=True)
    event_data = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)


# Export for init_db
all_models = [VoicebizUser, VoiceSession, VoiceInteraction,
              ValidationInteraction, VoiceAction, AuditLog]

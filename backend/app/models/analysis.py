"""SQLAlchemy ORM Model for immutable analysis snapshots.

A GramaVise Analysis represents an immutable point-in-time snapshot of what the
user submitted, what GramaVise calculated, what evidence was observed, and what
recommendations were generated.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class RecommendationStatusEnum(str, enum.Enum):
    PROCEED = "PROCEED"
    VALIDATE_FIRST = "VALIDATE_FIRST"
    RECONSIDER = "RECONSIDER"


class Analysis(Base):
    """Immutable persistent parent record for a completed feasibility analysis."""
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=True, index=True)

    # Provenance & Versioning
    schema_version = Column(String(20), default="1.0.0", nullable=False)
    rules_version = Column(String(20), default="1.0.0", nullable=False)

    # Core Verdict & Confidence
    recommendation_status = Column(Enum(RecommendationStatusEnum), default=RecommendationStatusEnum.VALIDATE_FIRST, nullable=False)
    overall_verdict = Column(String(50), nullable=True)
    confidence_score = Column(Float, default=0.0, nullable=False)

    # Immutable Point-in-Time Evaluation Snapshots (JSON / JSONB)
    business_input_snapshot = Column(JSON, default=dict, nullable=False)
    market_result_snapshot = Column(JSON, default=dict, nullable=False)
    scheme_result_snapshot = Column(JSON, default=dict, nullable=False)
    evidence_ledger_snapshot = Column(JSON, default=list, nullable=False)
    decision_trace_snapshot = Column(JSON, default=dict, nullable=False)
    action_plan_snapshot = Column(JSON, default=dict, nullable=False)
    bank_readiness_snapshot = Column(JSON, default=dict, nullable=False)
    risk_factors = Column(JSON, default=list, nullable=False)
    ai_explanation = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business = relationship("BusinessProfile", back_populates="analyses")
    financial_input_snapshot = relationship(
        "FinancialInputSnapshot",
        back_populates="analysis",
        uselist=False,
        cascade="all, delete-orphan",
    )
    financial_result_snapshot = relationship(
        "FinancialResultSnapshot",
        back_populates="analysis",
        uselist=False,
        cascade="all, delete-orphan",
    )
    scenarios = relationship(
        "ScenarioRecord",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="ScenarioRecord.created_at.asc()",
    )

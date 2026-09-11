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
    """Analysis audit log record storing structured evaluation results."""
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False, index=True)

    recommendation_status = Column(Enum(RecommendationStatusEnum), default=RecommendationStatusEnum.VALIDATE_FIRST, nullable=False)
    confidence_score = Column(Float, default=0.0, nullable=False)

    # Structured JSON payloads for modular components
    financial_result = Column(JSON, default=dict, nullable=False)
    market_result = Column(JSON, default=dict, nullable=False)
    scheme_result = Column(JSON, default=dict, nullable=False)
    risk_factors = Column(JSON, default=list, nullable=False)
    ai_explanation = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business = relationship("BusinessProfile", back_populates="analyses")

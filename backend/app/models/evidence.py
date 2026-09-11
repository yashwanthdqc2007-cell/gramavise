import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class EvidenceTypeEnum(str, enum.Enum):
    OBSERVED = "OBSERVED"
    CALCULATED = "CALCULATED"
    MODELLED = "MODELLED"
    ASSUMED = "ASSUMED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class LocalEvidence(Base):
    """Granular evidence item supporting feasibility recommendations."""
    __tablename__ = "local_evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False, index=True)

    indicator = Column(String(150), nullable=False)
    value = Column(String(150), nullable=False)
    unit = Column(String(50), nullable=True)
    evidence_type = Column(Enum(EvidenceTypeEnum), default=EvidenceTypeEnum.ASSUMED, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0

    source = Column(String(150), nullable=True)
    source_url = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business = relationship("BusinessProfile", back_populates="local_evidence")

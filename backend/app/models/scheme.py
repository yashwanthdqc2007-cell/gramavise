"""Government Scheme & Versioned Scheme Catalog ORM models."""
import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    JSON,
    DateTime,
    Text,
    ForeignKey,
    Enum as SqlEnum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class SchemeStatusEnum(str, enum.Enum):
    """Lifecycle status for a versioned government scheme definition."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"


class Scheme(Base):
    """Master Scheme entity representing a government assistance or credit program."""
    __tablename__ = "schemes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_code = Column(String(50), unique=True, index=True, nullable=False)
    scheme_name = Column(String(255), nullable=False)
    ministry = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Legacy fields maintained for backward compatibility where applicable
    ministry_or_dept = Column(String(255), nullable=True)
    max_loan_amount = Column(Float, default=0.0, nullable=True)
    subsidy_percentage_general = Column(Float, default=0.0, nullable=True)
    subsidy_percentage_special = Column(Float, default=0.0, nullable=True)
    interest_subvention_pct = Column(Float, default=0.0, nullable=True)
    eligibility_criteria = Column(JSON, default=dict, nullable=True)
    required_documents = Column(JSON, default=list, nullable=True)
    official_portal_url = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to immutable/versioned releases
    versions = relationship(
        "SchemeVersion",
        back_populates="scheme",
        cascade="all, delete-orphan",
        order_by="desc(SchemeVersion.created_at)",
    )


class SchemeVersion(Base):
    """Immutable versioned definition of a government scheme at a specific point in time."""
    __tablename__ = "scheme_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_code = Column(String(50), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    status = Column(
        SqlEnum(SchemeStatusEnum, name="schemestatusenum"),
        default=SchemeStatusEnum.ACTIVE,
        nullable=False,
        index=True,
    )

    description = Column(Text, nullable=True)
    official_source_name = Column(String(255), nullable=True)
    official_portal_url = Column(String(255), nullable=True)
    source_publication_date = Column(String(50), nullable=True)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    max_loan_amount = Column(Float, default=0.0, nullable=False)
    subsidy_percentage_general = Column(Float, default=0.0, nullable=False)
    subsidy_percentage_special = Column(Float, default=0.0, nullable=False)
    beneficiary_contribution_general_pct = Column(Float, default=0.0, nullable=False)
    beneficiary_contribution_special_pct = Column(Float, default=0.0, nullable=False)
    interest_subvention_pct = Column(Float, default=0.0, nullable=False)

    eligibility_criteria = Column(JSON, default=dict, nullable=False)
    required_documents = Column(JSON, default=list, nullable=False)
    verification_notes = Column(JSON, default=list, nullable=False)
    metadata_payload = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Master scheme relationship
    scheme = relationship("Scheme", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("scheme_code", "version", name="uq_scheme_version"),
    )


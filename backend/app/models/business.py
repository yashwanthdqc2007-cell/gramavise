import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class BusinessProfile(Base):
    """Business profile submitted for feasibility and advisory analysis."""
    __tablename__ = "business_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    business_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Location Details
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Entrepreneur Profile
    experience_years = Column(Integer, default=0, nullable=False)
    own_capital = Column(Float, default=0.0, nullable=False)
    desired_loan = Column(Float, default=0.0, nullable=False)
    is_new_business = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="businesses")
    financial_assumptions = relationship("FinancialAssumption", back_populates="business", cascade="all, delete-orphan")
    local_evidence = relationship("LocalEvidence", back_populates="business", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="business", cascade="all, delete-orphan")

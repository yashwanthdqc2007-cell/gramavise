import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class FinancialAssumption(Base):
    """Financial parameters and baseline assumptions associated with a business profile."""
    __tablename__ = "financial_assumptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False, index=True)

    # Initial Capex Breakdown
    startup_cost = Column(Float, default=0.0, nullable=False)
    equipment_cost = Column(Float, default=0.0, nullable=False)
    inventory_cost = Column(Float, default=0.0, nullable=False)

    # Operational Unit Economics
    monthly_fixed_cost = Column(Float, default=0.0, nullable=False)
    customers_per_day = Column(Integer, default=0, nullable=False)
    avg_ticket_price = Column(Float, default=0.0, nullable=False)
    working_days_per_month = Column(Integer, default=26, nullable=False)
    variable_cost_pct = Column(Float, default=0.0, nullable=False)  # As a percentage (e.g. 35.0 = 35%)

    # Financing Assumptions
    interest_rate_pct = Column(Float, default=10.0, nullable=False)  # Annual interest rate %
    loan_tenure_months = Column(Integer, default=36, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("BusinessProfile", back_populates="financial_assumptions")

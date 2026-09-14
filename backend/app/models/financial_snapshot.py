"""SQLAlchemy ORM models for immutable financial input and result snapshots.

These models capture the exact financial assumptions and deterministic calculation
results at evaluation time, guaranteeing historical immutability.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class FinancialInputSnapshot(Base):
    """Immutable snapshot of the 12 financial input assumptions used for an analysis."""
    __tablename__ = "financial_input_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # 1. Equity & Financing Outline
    own_capital = Column(Float, default=0.0, nullable=False)
    desired_loan = Column(Float, nullable=True)

    # 2-4. Capex Breakdown
    startup_cost = Column(Float, default=0.0, nullable=False)
    equipment_cost = Column(Float, default=0.0, nullable=False)
    inventory_cost = Column(Float, default=0.0, nullable=False)

    # 5-9. Operational Unit Economics
    monthly_fixed_cost = Column(Float, default=0.0, nullable=False)
    customers_per_day = Column(Integer, default=0, nullable=False)
    avg_ticket_price = Column(Float, default=0.0, nullable=False)
    working_days_per_month = Column(Integer, default=26, nullable=False)
    variable_cost_pct = Column(Float, default=0.0, nullable=False)

    # 10-12. Loan Terms
    interest_rate_pct = Column(Float, default=10.0, nullable=False)
    loan_tenure_months = Column(Integer, default=36, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="financial_input_snapshot")


class FinancialResultSnapshot(Base):
    """Immutable snapshot of the deterministic financial calculation results."""
    __tablename__ = "financial_result_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Capital Outlay & Debt
    total_capex = Column(Float, nullable=False)
    required_loan_amount = Column(Float, nullable=False)

    # Monthly Operating Metrics
    monthly_revenue = Column(Float, nullable=False)
    monthly_variable_cost = Column(Float, nullable=False)
    monthly_gross_profit = Column(Float, nullable=False)
    monthly_fixed_cost = Column(Float, nullable=False)
    monthly_emi = Column(Float, nullable=False)
    monthly_net_profit = Column(Float, nullable=False)
    net_profit_margin_pct = Column(Float, nullable=False)

    # Viability & Solvency Indicators
    break_even_revenue_monthly = Column(Float, nullable=False)
    break_even_units_daily = Column(Integer, nullable=False)
    dscr = Column(Float, nullable=False)
    is_financially_viable = Column(Boolean, nullable=False)

    # Declarative Explain-This-Number Metadata
    explanations = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="financial_result_snapshot")

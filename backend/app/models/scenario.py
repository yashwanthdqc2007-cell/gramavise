"""SQLAlchemy ORM Model for saved Scenario Records.

A ScenarioRecord captures a user-defined what-if parameter modification evaluated
against an immutable parent baseline Analysis.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ScenarioRecord(Base):
    """Persistent saved scenario belonging to a parent Analysis."""
    __tablename__ = "scenario_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(150), default="Custom Scenario", nullable=False)
    description = Column(Text, nullable=True)

    # Stored immutable snapshot of scenario inputs, results, and comparison deltas
    scenario_inputs = Column(JSON, default=dict, nullable=False)
    scenario_financial_result = Column(JSON, default=dict, nullable=False)
    scenario_recommendation = Column(JSON, default=dict, nullable=False)
    comparison_result = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="scenarios")

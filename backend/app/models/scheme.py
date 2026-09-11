import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, JSON, DateTime
from app.database import Base


class Scheme(Base):
    """Government financial scheme and credit assistance program entity."""
    __tablename__ = "schemes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_code = Column(String(50), unique=True, index=True, nullable=False)
    scheme_name = Column(String(255), nullable=False)
    ministry_or_dept = Column(String(255), nullable=True)

    max_loan_amount = Column(Float, default=0.0, nullable=False)
    subsidy_percentage_general = Column(Float, default=0.0, nullable=False)
    subsidy_percentage_special = Column(Float, default=0.0, nullable=False)
    interest_subvention_pct = Column(Float, default=0.0, nullable=False)

    eligibility_criteria = Column(JSON, default=dict, nullable=False)
    required_documents = Column(JSON, default=list, nullable=False)
    official_portal_url = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

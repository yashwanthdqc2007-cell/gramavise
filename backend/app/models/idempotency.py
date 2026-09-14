"""Idempotency Record ORM model for duplicate-request protection."""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    JSON,
    DateTime,
    UniqueConstraint,
)
from app.database import Base


class IdempotencyRecord(Base):
    """Stores request fingerprints and responses for state-modifying operations."""
    __tablename__ = "idempotency_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(128), index=True, nullable=False)
    scope = Column(String(50), index=True, nullable=False)  # e.g. "ANALYSIS", "SCENARIO"
    request_fingerprint = Column(String(64), nullable=False)  # Hex SHA-256
    resource_id = Column(String(36), index=True, nullable=True)  # Analysis.id or ScenarioRecord.id
    status = Column(String(20), default="COMPLETED", nullable=False)  # "IN_PROGRESS", "COMPLETED", "FAILED"
    response_payload = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("key", "scope", name="uq_idempotency_key_scope"),
    )

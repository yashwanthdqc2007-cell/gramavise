import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User entity representing micro-entrepreneurs or field operators."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    businesses = relationship("BusinessProfile", back_populates="user", cascade="all, delete-orphan")

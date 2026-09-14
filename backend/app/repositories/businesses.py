"""Business profile persistence repository."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.business import BusinessProfile
from app.repositories.base import AbstractRepository


class BusinessProfileRepository(AbstractRepository[BusinessProfile]):
    """Encapsulates database access and queries for BusinessProfile records."""

    def get_by_id(self, business_id: str) -> Optional[BusinessProfile]:
        stmt = select(BusinessProfile).where(BusinessProfile.id == business_id)
        return self.session.scalar(stmt)

    def list_for_user(self, user_id: str) -> List[BusinessProfile]:
        stmt = select(BusinessProfile).where(BusinessProfile.user_id == user_id).order_by(BusinessProfile.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def list_by_user(self, user_id: str) -> List[BusinessProfile]:
        """Alias for list_for_user."""
        return self.list_for_user(user_id)

    def add(self, business: BusinessProfile) -> BusinessProfile:
        self.session.add(business)
        return business

    def create(self, business: BusinessProfile) -> BusinessProfile:
        """Alias for add(). Transaction commit is governed by the Unit of Work."""
        return self.add(business)


# Retain alias for backwards compatibility
BusinessRepository = BusinessProfileRepository

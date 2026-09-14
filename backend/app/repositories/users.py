"""User persistence repository."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import AbstractRepository


class UserRepository(AbstractRepository[User]):
    """Encapsulates database access and queries for User records."""

    def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return self.session.scalar(stmt)

    def get_by_phone(self, phone_number: str) -> Optional[User]:
        stmt = select(User).where(User.phone_number == phone_number)
        return self.session.scalar(stmt)

    def add(self, user: User) -> User:
        self.session.add(user)
        return user

    def create(self, user: User) -> User:
        """Alias for add(). Persistence is committed by the Unit of Work."""
        return self.add(user)

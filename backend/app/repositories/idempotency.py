"""Idempotency Record persistence repository."""
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from app.models.idempotency import IdempotencyRecord
from app.repositories.base import AbstractRepository


class IdempotencyRepository(AbstractRepository[IdempotencyRecord]):
    """Encapsulates database access for IdempotencyRecord entities."""

    def get_by_id(self, entity_id: str) -> Optional[IdempotencyRecord]:
        """Fetch an idempotency record by primary key UUID."""
        return self.session.scalar(
            select(IdempotencyRecord).where(IdempotencyRecord.id == entity_id)
        )

    def get(self, key: str, scope: str) -> Optional[IdempotencyRecord]:
        """Fetch an existing idempotency record by key and operation scope."""
        stmt = select(IdempotencyRecord).where(
            and_(
                IdempotencyRecord.key == key,
                IdempotencyRecord.scope == scope,
            )
        )
        return self.session.scalar(stmt)

    def add(self, record: IdempotencyRecord) -> IdempotencyRecord:
        """Stage an IdempotencyRecord in active session."""
        self.session.add(record)
        return record

    def create(self, record: IdempotencyRecord) -> IdempotencyRecord:
        """Alias for add."""
        return self.add(record)

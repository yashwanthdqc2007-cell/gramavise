"""Base repository and Unit of Work interfaces for the persistence layer."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """Generic repository interface defining standard persistence operations."""

    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Retrieve an entity by primary key."""
        pass

    @abstractmethod
    def add(self, entity: T) -> T:
        """Stage an entity in the persistence session (does not commit)."""
        pass


class AbstractUnitOfWork(ABC):
    """Abstract Unit of Work managing transaction boundaries and session lifecycle."""

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        self.close()

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Roll back all uncommitted operations in the current transaction."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the underlying session."""
        pass

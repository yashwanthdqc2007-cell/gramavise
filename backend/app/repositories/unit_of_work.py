"""Unit of Work implementation providing transaction boundaries and session lifecycle management."""
from typing import Generator, Optional, Callable, Any
from sqlalchemy.orm import Session, sessionmaker

from app.database import SessionLocal
from app.repositories.base import AbstractUnitOfWork
from app.repositories.users import UserRepository
from app.repositories.businesses import BusinessProfileRepository
from app.repositories.analyses import AnalysisRepository
from app.repositories.snapshots import FinancialSnapshotRepository
from app.repositories.schemes import SchemeRepository
from app.repositories.scenarios import ScenarioRepository
from app.repositories.idempotency import IdempotencyRepository


class UnitOfWork(AbstractUnitOfWork):
    """Coordinates persistence operations and enforces single-transaction commit/rollback boundaries."""

    def __init__(
        self,
        session_factory: Optional[Callable[[], Session]] = None,
        existing_session: Optional[Session] = None,
    ):
        self._session_factory = session_factory or SessionLocal
        self._existing_session = existing_session
        self.session: Optional[Session] = None

        # Repository properties populated inside context
        self.users: Optional[UserRepository] = None
        self.business_profiles: Optional[BusinessProfileRepository] = None
        self.analyses: Optional[AnalysisRepository] = None
        self.snapshots: Optional[FinancialSnapshotRepository] = None
        self.schemes: Optional[SchemeRepository] = None
        self.scenarios: Optional[ScenarioRepository] = None
        self.idempotency: Optional[IdempotencyRepository] = None

    def __enter__(self) -> "UnitOfWork":
        if self._existing_session is not None:
            self.session = self._existing_session
            self._owns_session = False
        else:
            self.session = self._session_factory()
            self._owns_session = True

        self.users = UserRepository(self.session)
        self.business_profiles = BusinessProfileRepository(self.session)
        self.businesses = self.business_profiles  # Alias
        self.analyses = AnalysisRepository(self.session)
        self.snapshots = FinancialSnapshotRepository(self.session)
        self.schemes = SchemeRepository(self.session)
        self.scenarios = ScenarioRepository(self.session)
        self.idempotency = IdempotencyRepository(self.session)

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        if self._owns_session and self.session is not None:
            self.close()

    def commit(self) -> None:
        """Commit all staged operations within the active transaction."""
        if self.session is not None:
            self.session.commit()

    def rollback(self) -> None:
        """Roll back all operations in the active transaction."""
        if self.session is not None:
            self.session.rollback()

    def close(self) -> None:
        """Close the active SQLAlchemy session."""
        if self.session is not None:
            self.session.close()


def get_uow() -> Generator[UnitOfWork, None, None]:
    """FastAPI dependency provider yielding a managed UnitOfWork instance."""
    with UnitOfWork() as uow:
        yield uow

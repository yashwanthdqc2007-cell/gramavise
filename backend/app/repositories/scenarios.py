"""Scenario persistence repository.

Provides create and query access for saved ScenarioRecord entities against a parent
Analysis. Strictly enforces the maximum limit of 3 saved scenarios per analysis.
"""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.models.scenario import ScenarioRecord
from app.repositories.base import AbstractRepository


class ScenarioLimitExceededError(ValueError):
    """Raised when attempting to save more than 3 scenarios for a single parent analysis."""
    pass


class ScenarioRepository(AbstractRepository[ScenarioRecord]):
    """Encapsulates database access for immutable ScenarioRecord entities."""

    def get_by_id(self, scenario_id: str) -> Optional[ScenarioRecord]:
        """Retrieve a scenario by primary key."""
        stmt = select(ScenarioRecord).where(ScenarioRecord.id == scenario_id)
        return self.session.scalar(stmt)

    def list_by_analysis(self, analysis_id: str) -> List[ScenarioRecord]:
        """List all saved scenarios for a specific parent analysis ordered by creation time."""
        stmt = (
            select(ScenarioRecord)
            .where(ScenarioRecord.analysis_id == analysis_id)
            .order_by(ScenarioRecord.created_at.asc())
        )
        return list(self.session.scalars(stmt).all())

    def count_by_analysis(self, analysis_id: str) -> int:
        """Count existing saved scenarios for a specific parent analysis."""
        stmt = select(func.count()).select_from(ScenarioRecord).where(ScenarioRecord.analysis_id == analysis_id)
        return int(self.session.scalar(stmt) or 0)

    def add(self, scenario: ScenarioRecord, lock_parent: bool = True) -> ScenarioRecord:
        """Stage a ScenarioRecord in the session after enforcing the 3-scenario limit.
        
        Concurrency strategy:
        Acquires a row-level lock (FOR UPDATE) on the parent Analysis row in PostgreSQL to
        serialize concurrent creation attempts for the same parent analysis and prevent
        count-check race conditions.
        """
        if lock_parent:
            stmt_lock = select(Analysis.id).where(Analysis.id == scenario.analysis_id).with_for_update()
            self.session.execute(stmt_lock)

        current_count = self.count_by_analysis(scenario.analysis_id)
        if current_count >= 3:
            raise ScenarioLimitExceededError(
                f"Maximum limit of 3 saved scenarios reached for parent analysis '{scenario.analysis_id}'."
            )
        self.session.add(scenario)
        return scenario


    def create(self, scenario: ScenarioRecord) -> ScenarioRecord:
        """Alias for add(). Transaction commits are owned by the Unit of Work."""
        return self.add(scenario)

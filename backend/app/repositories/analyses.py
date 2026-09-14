"""Analysis persistence repository.

Provides create and query access for immutable Analysis records and their
associated financial snapshots. Does not provide update or overwrite operations.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.analysis import Analysis
from app.models.financial_snapshot import FinancialInputSnapshot, FinancialResultSnapshot
from app.repositories.base import AbstractRepository


class AnalysisRepository(AbstractRepository[Analysis]):
    """Encapsulates persistence and query logic for immutable Analysis records."""

    def get_by_id(self, analysis_id: str) -> Optional[Analysis]:
        """Retrieve an Analysis by ID with eagerly loaded financial snapshots."""
        stmt = (
            select(Analysis)
            .where(Analysis.id == analysis_id)
            .options(
                joinedload(Analysis.financial_input_snapshot),
                joinedload(Analysis.financial_result_snapshot),
            )
        )
        return self.session.scalar(stmt)

    def list_by_business(self, business_id: str) -> List[Analysis]:
        """List historical analyses for a specific business profile ordered by creation time."""
        stmt = (
            select(Analysis)
            .where(Analysis.business_id == business_id)
            .options(
                joinedload(Analysis.financial_input_snapshot),
                joinedload(Analysis.financial_result_snapshot),
            )
            .order_by(Analysis.created_at.desc())
        )
        return list(self.session.scalars(stmt).unique().all())

    def add(self, analysis: Analysis) -> Analysis:
        """Stage an Analysis entity in the session."""
        self.session.add(analysis)
        return analysis

    def create(
        self,
        analysis: Analysis,
        input_snapshot: Optional[FinancialInputSnapshot] = None,
        result_snapshot: Optional[FinancialResultSnapshot] = None,
    ) -> Analysis:
        """Stage an Analysis and its associated 1-to-1 financial snapshots atomically.
        
        Commit/rollback is governed exclusively by the Unit of Work.
        """
        self.session.add(analysis)
        if input_snapshot is not None:
            input_snapshot.analysis_id = analysis.id
            self.session.add(input_snapshot)
        if result_snapshot is not None:
            result_snapshot.analysis_id = analysis.id
            self.session.add(result_snapshot)
        return analysis

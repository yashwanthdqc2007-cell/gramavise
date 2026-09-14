"""Financial snapshot persistence repository."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.financial_snapshot import FinancialInputSnapshot, FinancialResultSnapshot


class FinancialSnapshotRepository:
    """Encapsulates querying and direct staging of financial input and result snapshots."""

    def __init__(self, session: Session):
        self.session = session

    def get_input_by_analysis_id(self, analysis_id: str) -> Optional[FinancialInputSnapshot]:
        stmt = select(FinancialInputSnapshot).where(FinancialInputSnapshot.analysis_id == analysis_id)
        return self.session.scalar(stmt)

    def get_result_by_analysis_id(self, analysis_id: str) -> Optional[FinancialResultSnapshot]:
        stmt = select(FinancialResultSnapshot).where(FinancialResultSnapshot.analysis_id == analysis_id)
        return self.session.scalar(stmt)

    def add_input_snapshot(self, snapshot: FinancialInputSnapshot) -> FinancialInputSnapshot:
        self.session.add(snapshot)
        return snapshot

    def add_result_snapshot(self, snapshot: FinancialResultSnapshot) -> FinancialResultSnapshot:
        self.session.add(snapshot)
        return snapshot

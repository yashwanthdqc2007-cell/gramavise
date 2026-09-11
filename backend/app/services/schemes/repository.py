from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.scheme import Scheme


class SchemeRepository:
    """Persistence layer for Government Schemes data."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Scheme]:
        """TODO [Database Lead]: Query active schemes from DB table."""
        return self.db.query(Scheme).all()

    def get_by_code(self, scheme_code: str) -> Optional[Scheme]:
        """TODO [Database Lead]: Query single scheme by code."""
        return self.db.query(Scheme).filter(Scheme.scheme_code == scheme_code).first()

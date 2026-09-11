from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.analysis import Analysis


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, analysis_id: str) -> Optional[Analysis]:
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def list_by_business(self, business_id: str) -> List[Analysis]:
        return self.db.query(Analysis).filter(Analysis.business_id == business_id).all()

    def create(self, analysis: Analysis) -> Analysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

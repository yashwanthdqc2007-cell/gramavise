from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.scheme import Scheme


class SchemeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[Scheme]:
        return self.db.query(Scheme).all()

    def get_by_code(self, scheme_code: str) -> Optional[Scheme]:
        return self.db.query(Scheme).filter(Scheme.scheme_code == scheme_code).first()

    def create(self, scheme: Scheme) -> Scheme:
        self.db.add(scheme)
        self.db.commit()
        self.db.refresh(scheme)
        return scheme

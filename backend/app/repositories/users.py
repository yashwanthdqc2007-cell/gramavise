from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.analysis import Analysis
from app.models.scheme import Scheme


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_phone(self, phone_number: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone_number == phone_number).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class BusinessRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, business_id: str) -> Optional[BusinessProfile]:
        return self.db.query(BusinessProfile).filter(BusinessProfile.id == business_id).first()

    def list_by_user(self, user_id: str) -> List[BusinessProfile]:
        return self.db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).all()

    def create(self, business: BusinessProfile) -> BusinessProfile:
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business


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


class SchemeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[Scheme]:
        return self.db.query(Scheme).all()

    def get_by_code(self, scheme_code: str) -> Optional[Scheme]:
        return self.db.query(Scheme).filter(Scheme.scheme_code == scheme_code).first()

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.business import BusinessProfile


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

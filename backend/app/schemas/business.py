from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class LocationSchema(BaseModel):
    state: str = Field(..., description="State name (e.g. Uttar Pradesh, Maharashtra)")
    district: str = Field(..., description="District name")
    village: str = Field(..., description="Village or Gram Panchayat / Town name")
    latitude: Optional[float] = Field(None, description="GPS Latitude coordinate")
    longitude: Optional[float] = Field(None, description="GPS Longitude coordinate")


class BusinessProfileBase(BaseModel):
    business_name: str = Field(..., description="Proposed or existing business title")
    category: str = Field(..., description="Business category (e.g. Kirana, Atta Chakki, Dairy, Poultry, Tailoring)")
    description: Optional[str] = Field(None, description="Brief description of enterprise activities")
    location: LocationSchema
    experience_years: int = Field(0, ge=0, description="Years of entrepreneur experience in domain")
    own_capital: float = Field(0.0, ge=0.0, description="Available own equity/savings in INR")
    desired_loan: float = Field(0.0, ge=0.0, description="Desired bank loan in INR")
    is_new_business: bool = Field(True, description="True if new unit, False if expansion")


class BusinessProfileCreate(BusinessProfileBase):
    user_id: Optional[str] = None


class BusinessProfileResponse(BusinessProfileBase):
    id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

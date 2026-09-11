from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    phone_number: str = Field(..., description="10-digit mobile number")
    full_name: Optional[str] = Field(None, description="Full name of entrepreneur or operator")
    preferred_language: str = Field("en", description="ISO 639-1 language code (en, hi, mr, bn, te, ta)")


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

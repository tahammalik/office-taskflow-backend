from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CreateEnterprise(BaseModel):
    name: str
    email: EmailStr

class ResponseEnterprise(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateEnterprise(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

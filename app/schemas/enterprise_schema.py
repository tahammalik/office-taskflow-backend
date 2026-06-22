from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


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
    name: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]

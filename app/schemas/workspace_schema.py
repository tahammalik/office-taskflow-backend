from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class CreateWorkspace(BaseModel):
    name: str
    email: EmailStr


class ResponseWorkspace(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateWorkspace(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]

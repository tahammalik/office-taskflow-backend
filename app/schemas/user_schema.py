from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str
    token: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    workspace_id: Optional[int] = None
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    workspace_id: Optional[int] = None


class UserMinRead(BaseModel):
    id: int
    username: str
    workspace_id: int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

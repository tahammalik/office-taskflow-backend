from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    enterprise_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    enterprise_id: Optional[int] = None

class UserMinRead(BaseModel):
    id: int
    username: str
    enterprise_id:int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, EmailStr
import typing as t
import datetime

class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = t.Literal["manager", "user"]

class InvitationDB(BaseModel):
    id: int
    email: EmailStr
    role: str
    token: str
    enterprise_id: int
    invited_by: int
    status: t.Literal["pending", "accepted", "declined"]
    expires_at: datetime

    class Config:
        orm_mode = True

class InvitationResponse(BaseModel):
    id: int
    invited_email: EmailStr
    role: str
    status: t.Literal["pending", "accepted", "declined"]

    class Config:
        orm_mode = True
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class CreateInvitation(BaseModel):
    email: EmailStr
    role: str = "user"  # "user" or "manager" — restrict at validation if needed


class ResponseInvitation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    workspace_id: int
    role: str
    status: str = "pending"  # "pending", "accepted", or "declined"
    created_at: datetime
    expires_at: datetime


class AcceptInvitation(BaseModel):
    token: str
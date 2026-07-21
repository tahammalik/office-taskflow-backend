from datetime import datetime
from typing import Optional,List
from app.schemas.project_schema import ProjectResponse
from app.schemas.team_schema import TeamResponse
from app.schemas.user_schema import UserResponse
from pydantic import BaseModel, EmailStr,ConfigDict


class CreateWorkspace(BaseModel):
    name: str
    email: EmailStr


class ResponseWorkspace(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    teams:List[TeamResponse] = []
    projects:List[ProjectResponse] = []
    users: List[UserResponse] = []


    class Config:
        model_config = ConfigDict(from_attributes=True)


class UpdateWorkspace(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]

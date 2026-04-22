from pydantic import BaseModel, ConfigDict,Field
from datetime import datetime
from typing import Optional
from app.schemas.user_schema import UserMinRead


class CreateProject(BaseModel):

    title: str
    description: str
    dead_line: datetime

class UpdateProject(BaseModel):

    title: Optional[str]
    description: Optional[str]
    dead_line: Optional[datetime]

class ProjectResponse(BaseModel):
    
    id: int
    title: str
    description: str
    starting_at: datetime
    dead_line: datetime
    created_by: UserMinRead = Field(alias='creator')

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict,Field
from datetime import datetime
from typing import Optional,Literal
from app.schemas.team_schema import TeamRead
from app.schemas.user_schema import UserMinRead


class CreateProject(BaseModel):

    title: str
    description: str
    deadline: datetime
    status: Literal["planning", "active", "on_hold","review", "completed", "archived"]

# update project model for optional fields
class UpdateProject(BaseModel):

    title: Optional[str]
    description: Optional[str]
    deadline: Optional[datetime]

# response model for project details with teams and creator details
class ProjectResponse(BaseModel):
    
    id: int
    title: str
    description: str
    starting_at: datetime
    deadline: datetime
    teams: list[TeamRead] = []  # return list of teams assigned to this project 
    created_by: UserMinRead = Field(alias='created_by') # return creator details in response

    model_config = ConfigDict(from_attributes=True)

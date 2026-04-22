from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.user_schema import UserMinRead

class CreateTeam(BaseModel):

    id: int
    team_name: str
    description: Optional[str]
    

class TeamResponse(BaseModel):
    
    id: int
    team_name: str
    description: Optional[str]
    created_at: datetime
    project_id: int
    leader: UserMinRead
    tasks: Optional[list] = []

    model_config = ConfigDict(from_attributes=True)

class TeamUpdate(BaseModel):
    
    team_name: Optional[str]
    description: Optional[str]
    project_id: Optional[int]
    leader_id: Optional[int]
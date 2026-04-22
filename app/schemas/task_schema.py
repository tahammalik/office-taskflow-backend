from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.user_schema import UserMinRead
from typing import Literal

# schema for create task
class CreateTask(BaseModel):

    title: str = Field(...,max_length=50)
    description: Optional[str] = Field(None)
    assign_to: int              # param:id so datatype is int
    status: Literal['todo', 'in_progress', 'review', 'done']
# Task response schema
class ResponseTask(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    assigned_employee: UserMinRead
    creator_manager: UserMinRead

    model_config = ConfigDict(from_attributes=True)
    

# Task update schema
class TaskUpdate(BaseModel):

    title: Optional[str] = None
    description: Optional[str] = None
    assign_to: Optional[int] = None     # param:id so datatype is int
    status: str = Field(Literal['todo', 'in_progress', 'review', 'done'])



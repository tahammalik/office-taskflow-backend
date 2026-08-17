from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user_schema import UserMinRead


# schema for create task
class CreateTask(BaseModel):
    title: str = Field(..., max_length=50)
    description: str
    status: Literal["pending", "in_progress", "review", "completed"]
    dead_line: datetime
    team_id: int
    assign_to: int  # user id of the employee to whom the task is assigned

class TaskHistory(BaseModel):
    task_id: int
    changed_by: int
    old_status: str
    new_status: str
    comment: str
    changed_at: datetime

class TaskHistoryRead(BaseModel):
    id: int
    task_id: int
    changed_by: int
    old_status: str
    new_status: str
    comment: str
    changed_at: datetime

# Task response schema
class ResponseTask(BaseModel):
    id: int
    title: str
    description: str
    status: str
    assigned_employee: UserMinRead
    creator_manager: UserMinRead
    history: list[TaskHistoryRead] = []

    model_config = ConfigDict(from_attributes=True)


# Task update schema
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assign_to: Optional[int] = None  # param:id so datatype is int
    status: Optional[Literal["pending", "in_progress", "review", "completed"]] = None
    status_comment: Optional[str] = ""
    dead_line: datetime | None = None


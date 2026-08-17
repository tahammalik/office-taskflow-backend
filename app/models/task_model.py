import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db import Base

class TaskStatus(str, enum.Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    REVIEW = 'review'
    COMPLETED = 'completed'

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus, name='task_status_enum'), nullable=False, default=TaskStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('teams.id'), nullable=False)
    assign_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey('workspaces.id'), nullable=False)

    team = relationship('Team', back_populates='tasks', passive_deletes=True)
    assigned_employee = relationship('User', foreign_keys='Task.assign_to', back_populates='assigned_tasks')
    creator_manager = relationship('User', foreign_keys='Task.created_by', back_populates='created_tasks')

    history = relationship('TaskHistory',back_populates='detail')
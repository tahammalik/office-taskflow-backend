import enum
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class TaskStatus(str,enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(SAEnum(TaskStatus,name ="task_status_enum"), nullable=False,default=TaskStatus.PENDING)

    created_at = Column(DateTime, server_default=func.now())
    deadline = Column(DateTime,nullable=False)
    updated_at = Column(DateTime,server_default=func.now(), onupdate=func.now(),default=None)
    is_deleted = Column(Boolean, default=False)
    # Foreign Keys
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    assign_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)

    # Relationships
    team = relationship('Team', back_populates='tasks',passive_deletes=True)
    assigned_employee = relationship('User', foreign_keys='Task.assign_to',
                                     back_populates='assigned_tasks')
    creator_manager = relationship('User',foreign_keys='Task.created_by',
                                   back_populates='created_tasks')
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Association table for Project and Team (Many-to-Many)
ProjectTeams = Table(
    'project_teams',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True)
)

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(SAEnum(ProjectStatus, name='project_status_enum'), nullable=False, default=ProjectStatus.PLANNING)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey('workspaces.id'), index=True)

    workspace = relationship('Workspace', back_populates='projects')
    teams = relationship('Team', secondary='project_teams', back_populates='projects')
    history = relationship('ProjectHistory', back_populates='project')
    initiator = relationship('User',back_populates='project_initiator')

class ProjectHistory(Base):
    __tablename__ = 'project_histories'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    changed_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False, index=True)

    project = relationship('Project', back_populates='history')
    user = relationship('User', back_populates='project_history')

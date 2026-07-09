from sqlalchemy import (Column,Integer,String,
                        DateTime,ForeignKey,
                        func, Table,Boolean, Text)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum

# Association table for Project and Team (Many-to-Many)
ProjectTeams = Table(
    'project_teams',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True)
)

class ProjectStatus(str,enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    status = Column(SAEnum(ProjectStatus,name='project_status_enum'),nullable=False,default=ProjectStatus.PLANNING)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'),index=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'),index=True)

    # Relationships
    workspace = relationship('Workspace', back_populates='projects')
    teams = relationship('Team', secondary="project_teams", back_populates='projects')
    history = relationship('ProjectHistory',back_populates='project')

class ProjectHistory(Base):
    __tablename__ = "project_histories"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False,index=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    field_name = Column(String(50), nullable=False)   # e.g., "status", "title"
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=func.now(), nullable=False,index=True)

    # Relationships
    project = relationship("Project", back_populates="history")
    user = relationship("User", back_populates="project_history")
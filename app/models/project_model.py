from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Table, Boolean
from sqlalchemy.orm import relationship
from app.core.db import Base

# Association table for Project and Team (Many-to-Many)
ProjectTeams = Table(
    'project_teams',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True)
)

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    deadline = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))

    # Relationships
    workspace = relationship('Workspace', back_populates='projects')
    teams = relationship('Team', secondary="project_teams", back_populates='projects')

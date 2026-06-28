from sqlalchemy import Column, Integer, String, Boolean, DateTime, UniqueConstraint, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class TeamMember(Base):
    __tablename__ = 'team_members'

    team_id = Column(Integer, ForeignKey('teams.id'),primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    joined_at = Column(DateTime, default=func.now())


class Team(Base):
    __tablename__ = 'teams'

    __table_args__ = (
        UniqueConstraint('team_name', 'workspace_id', name='uq_team_name_workspace'),
    )

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String,index=True, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    workspace = relationship('Workspace')
    leader = relationship('User', back_populates='led_teams')
    tasks = relationship('Task', back_populates='team',cascade="all, delete-orphan")
    projects = relationship('Project', secondary='project_teams', back_populates='teams')

    members = relationship('User', secondary='team_members', back_populates='teams')
"""
    this file handles group
"""

from sqlalchemy import String,Integer,DateTime,Column,ForeignKey,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
from . import project_model
class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String,nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean,nullable=False,default=True)
    is_deleted = Column(Boolean,nullable=False,default=False)
    organization_id = Column(Integer,ForeignKey('organizations.id'),nullable=True)
    # leader id
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # Relationships
    project = relationship('Project',secondary=project_model.ProjectTeams.__table__,back_populates='teams')
    leader = relationship('User',foreign_keys='Team.leader_id', back_populates='team_led')
    tasks = relationship('Task', back_populates='team')
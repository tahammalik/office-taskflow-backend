"""
    this file handles group
"""

from sqlalchemy import String,Integer,DateTime,Column,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String,nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    # Foreign Keys
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    project = relationship('Project', back_populates='teams')
    leader = relationship('User',foreign_keys='Team.leader_id', back_populates='team_led')
    tasks = relationship('Task', back_populates='team')
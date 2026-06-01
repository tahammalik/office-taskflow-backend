from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    enterprise_id = Column(Integer, ForeignKey('enterprises.id'), nullable=True)
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationships
    enterprise = relationship('Enterprise')
    leader = relationship('User', back_populates='led_teams')
    tasks = relationship('Task', back_populates='team')
    projects = relationship('Project', secondary='project_teams', back_populates='teams')

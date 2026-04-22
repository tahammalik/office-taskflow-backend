from sqlalchemy import String,Integer,DateTime,Column,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    starting_at = Column(DateTime, server_default=func.now())
    dead_line = Column(DateTime)
    created_by = Column(Integer, ForeignKey('users.id'))
    organization_id = Column(Integer,ForeignKey('organizations.id'))

    # Relationships
    creator = relationship('User', foreign_keys=[created_by], back_populates='projects_created')
    teams = relationship('Team', back_populates='project')
    organization = relationship('Organization',back_populates='projects')

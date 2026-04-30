from sqlalchemy import String,Integer,DateTime,Column,ForeignKey,Boolean,Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

# association table for many to many relationship between project and team
class ProjectTeams(Base):
    __tablename__ = 'project_teams'

    project_id = Column(Integer, ForeignKey('projects.id'),primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'),primary_key=True)

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    starting_at = Column(DateTime, server_default=func.now())
    dead_line = Column(DateTime,nullable=False)
    is_deleted = Column(Boolean, nullable=False,default=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    organization_id = Column(Integer,ForeignKey('organizations.id'))

    # Relationships
    creator = relationship('User', foreign_keys=[created_by], back_populates='projects_created')
    teams = relationship('Team',secondary=ProjectTeams.__table__,back_populates='project')
    organization = relationship('Organization',back_populates='projects')




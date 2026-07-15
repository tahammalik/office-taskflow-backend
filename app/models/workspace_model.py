from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class Workspace(Base):
    __tablename__ = 'workspaces'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey('users.id', use_alter=True,name='fk_workspace_created_by'), nullable=True)

    # relationship
    projects = relationship('Project', back_populates='workspace')
    users = relationship('User', foreign_keys='User.workspace_id', back_populates='workspace')
    teams = relationship('Team',foreign_keys='Team.workspace_id',back_populates='workspace')
    

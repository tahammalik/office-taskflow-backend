"""
   This file for maintaining user table related
   operations
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default='user') # CEO, Manager, Leader, Employee
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)

    # Relationships
    organization = relationship('Organization',foreign_keys=[organization_id],back_populates='users')
    projects_created = relationship('Project', back_populates='creator')
    team_led = relationship('Team', back_populates='leader')
    tasks_assigned = relationship('Task', foreign_keys='Task.assign_to', back_populates='assigned_employee')
    tasks_creator = relationship('Task', foreign_keys='Task.created_by', back_populates='creator_manager')

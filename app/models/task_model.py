from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String,nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    dead_line = Column(DateTime)

    # Foreign Keys
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    assign_to = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    team = relationship('Team', back_populates='tasks')
    assigned_employee = relationship('User', foreign_keys='Task.assign_to',
                                     back_populates='tasks_assigned')
    # creator_manager who create the task can be manager leader or admin
    creator_manager = relationship('User',foreign_keys='Task.created_by',
                                   back_populates='tasks_creator')
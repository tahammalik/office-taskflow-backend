from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    enterprise_id = Column(Integer, ForeignKey('enterprises.id'), default=None)

    # Relationships
    enterprise = relationship('Enterprise', foreign_keys=[enterprise_id], back_populates='users')
    created_tasks = relationship('Task', foreign_keys='Task.created_by', back_populates='creator_manager')
    assigned_tasks = relationship('Task', foreign_keys='Task.assign_to', back_populates='assigned_employee')
    led_teams = relationship('Team', back_populates='leader')

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Enterprise(Base):
    __tablename__ = 'enterprises'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))

    # relationship
    projects = relationship('Project', back_populates='enterprise')
    users = relationship('User', foreign_keys='User.enterprise_id', back_populates='enterprise')

from sqlalchemy import String, Integer, DateTime, Column, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)


    # define relationships
    projects = relationship('Project', back_populates='organization')
    users = relationship('User',foreign_keys='User.organization_id',back_populates='organization')
    creator = relationship('User',foreign_keys=[created_by])


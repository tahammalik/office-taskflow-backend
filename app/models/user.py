"""
   This file for maintaining user table related
   operations
"""
from sqlalchemy import Column,String,Boolean,Integer
from app.core.db import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,autoincrement=True,index=True)
    username = Column(String,nullable=False,unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
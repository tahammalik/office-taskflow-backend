"""
    This file for maintaining database
    database connections etc.
"""

from typing import Annotated
from fastapi.params import Depends
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

conn_url = URL.create(
    drivername='postgresql',
    username='taham',
    password='taham2007@',
    host='localhost',
    port=5432,
    database='userdb'
)

engine = create_engine(conn_url)

sessionlocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = sessionlocal()
    try:
        yield db

    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

"""
    -------database module-------

    This file for maintaining database
    database connections and sessions.
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

try:
    engine = create_engine(conn_url)
except Exception as e:
    raise ConnectionError(f"Failed to connect to the database: {e}")


sessionlocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = sessionlocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

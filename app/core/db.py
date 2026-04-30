"""
    -------database module-------

    This file for maintaining database
    database connections and sessions.
"""

from typing import Annotated
from fastapi.params import Depends
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.core.config import DatabaseConfig
from app.core.logging_config import get_logger

logger = get_logger(__name__)

db_config = DatabaseConfig()

engine = create_engine(db_config.build_connection(),pool_size=10,pool_timeout=1800)

try:
    with engine.connect() as conn:
        logger.info("Engine Connected %s", conn)
except Exception as e:
    logger.error(f"Engine Error: %s",e)

sessionlocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = sessionlocal()
    try:
        yield db
    except:
        db.rollback()
        raise 
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

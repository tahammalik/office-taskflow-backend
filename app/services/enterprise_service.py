from app.schemas.enterprise_schema import CreateEnterprise
from app.core.db import db_dependency
from app.models.enterprise_model import Enterprise
from fastapi import HTTPException,status
from logging import getLogger

logger = getLogger(__name__)

def add_enterprise(enterprise_data:CreateEnterprise,user_id:int,db:db_dependency):

    new_enterprise = Enterprise(
        name = enterprise_data.name,
        email = enterprise_data.email,
        created_by = user_id
    )

    try:
        db.add(new_enterprise)
        db.commit()
        db.refresh(new_enterprise)
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    
    return new_enterprise

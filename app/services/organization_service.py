from app.schemas.organization_schema import CreateOrganization
from app.core.db import db_dependency
from app.models.organization_model import Organization
from fastapi import HTTPException,status
from logging import getLogger

logger = getLogger(__name__)

def add_organization(org_data:CreateOrganization,user_id:int,db:db_dependency):

    new_organization = Organization(
        name = org_data.name,
        created_by = user_id
    )

    try:
        db.add(new_organization)
        db.commit()
        db.refresh(new_organization)
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    
    return new_organization
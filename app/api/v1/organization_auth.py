from fastapi import APIRouter,HTTPException,status
from app.core.db import db_dependency
from app.schemas.organization_schema import CreateOrganization
from app.services.organization_service import add_organization
from app.models.user_model import User
from fastapi import Depends
from app.core.dependencies import get_current_user
from app.models.organization_model import Organization
from app.core.logging_config import get_logger
from app.core.dependencies import require_role


router = APIRouter(
    prefix='/v1/organization',
    tags=['Organization']
)

logger = get_logger(__name__)

# Create new Organization
@router.post('/create')
async def create_organization(org_data:CreateOrganization,db:db_dependency,
                              current_user: User = Depends(get_current_user)):
    search_org = db.query(Organization).filter(Organization.email == org_data.email).first()
    if search_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this email already exists")
    new_organization = Organization(name = org_data.name,email=org_data.email,
                                    created_by = current_user.id)
    try:
        db.add(new_organization)
        db.query(User).filter(User.id == current_user.id).update({"role":"admin",
                                                "organization_id":new_organization.id})
        db.commit()
        db.refresh(new_organization)
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred")
    
    return new_organization

# Organization deletion
@router.delete('/delete/{org_id}',dependencies=[Depends(require_role(['admin']))])
async def delete_organization(org_id:int,db:db_dependency,
                              current_user: User = Depends(get_current_user)):

    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found")
    if organization.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is already inactive")
    try:
        db.query(Organization).filter(Organization.id == current_user.organization_id).update({"is_active": False})
        db.query(User).filter(User.organization_id == org_id).update({"organization_id": None,"role": "user"})
        db.commit()
        logger.info(f"Organization {org_id} deleted successfully.")
        return {"message": "Organization and memberships cleared."}
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(status_code=500, detail='Database error occurred')
    



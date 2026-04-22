from fastapi import APIRouter,HTTPException,status
from app.core.db import db_dependency
from app.schemas.organization_schema import CreateOrganization
from app.services.organization_service import add_organization
from app.models.user_model import User
from fastapi import Depends
from app.core.dependencies import get_current_user
from app.models.organization_model import Organization
from logging import getLogger
from app.core.dependencies import require_role


router = APIRouter(
    prefix='/org/login',
    tags=['Organization']
)

logger = getLogger(__name__)

# Create new Organization
@router.post('/')
async def create_organization(org_data:CreateOrganization,db:db_dependency,
                current_user: User = Depends(get_current_user)):

    new_org = add_organization(org_data,current_user.id,db=db)

    try:
        db.query(User).filter(User.id == current_user.id).update(
            {
                "role":"admin",
                "organization_id":new_org.id
            }
        )

        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(status_code=500, detail='Database error occurred') # problem here.

    
    return new_org

# Organization deletetion 
@router.delete('/delete/{org_id}',dependencies=[Depends(require_role(['admin']))])
async def delete_organization(org_id:int,db:db_dependency):

    organization = db.query(Organization).filter(Organization.id == org_id).first()

    if not organization:
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    try:
        db.query(User).filter(User.organization_id == org_id).update(
        {
            "organization_id": None,
            "role": "user"
        })

        db.delete(organization)
        db.commit()
        logger.info(f"Organization {org_id} deleted successfully.")
        return {"message": "Organization and memberships cleared."}
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(status_code=500, detail='Database error occurred')
    



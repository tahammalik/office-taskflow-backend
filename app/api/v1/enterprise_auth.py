from fastapi import APIRouter,HTTPException,status, Depends
from app.core.db import db_dependency
from app.schemas.enterprise_schema import CreateEnterprise, ResponseEnterprise
from app.models.user_model import User
from app.core.dependencies import get_current_user
from app.models.enterprise_model import Enterprise
from app.core.logging_config import get_logger
from app.core.dependencies import require_role


router = APIRouter(
    prefix='/v1/enterprise',
    tags=['Enterprise']
)

logger = get_logger(__name__)

# Create new Enterprise
@router.post('/create', response_model=ResponseEnterprise)
async def create_enterprise(enterprise_data:CreateEnterprise,db:db_dependency,
                              current_user: User = Depends(get_current_user)):
    search_ent = db.query(Enterprise).filter(Enterprise.email == enterprise_data.email).first()
    if search_ent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise with this email already exists")
    new_enterprise = Enterprise(name = enterprise_data.name,email=enterprise_data.email,
                                    created_by = current_user.id)
    try:
        db.add(new_enterprise)
        db.flush()
        db.query(User).filter(User.id == current_user.id).update({"role":"admin",
                                                "enterprise_id":new_enterprise.id})
        db.commit()
        db.refresh(new_enterprise)
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred")
    
    return new_enterprise

# Enterprise deletion
@router.delete('/delete/{ent_id}',dependencies=[Depends(require_role(['admin']))])
async def delete_enterprise(ent_id:int,db:db_dependency,
                              current_user: User = Depends(get_current_user)):
    
    if current_user.enterprise_id != ent_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have administrative authority over this enterprise.")
    
    enterprise = db.query(Enterprise).filter(Enterprise.id == ent_id).first()
    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found")
    if enterprise.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise is already inactive")
    try:
        db.query(Enterprise).filter(Enterprise.id == ent_id).update({"is_active": False})
        db.query(User).filter(User.enterprise_id == ent_id).update({"enterprise_id": None,"role": "user"})
        db.commit()
        logger.info(f"Enterprise {ent_id} deleted successfully.")
        return {"message": "Enterprise and memberships cleared."}
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(status_code=500, detail='Database error occurred')

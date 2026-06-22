from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select,update
from app.core.db import db_dependency
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger
from app.models.enterprise_model import Enterprise
from app.models.user_model import User
from app.schemas.enterprise_schema import CreateEnterprise, ResponseEnterprise

router = APIRouter(prefix="/v1/enterprise", tags=["Enterprise"])

logger = get_logger(__name__)


# Create new Enterprise
@router.post("/create", response_model=ResponseEnterprise)
async def create_enterprise(
    enterprise_data: CreateEnterprise,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    # search for email is already exist or not
    result =  await db.execute(select(Enterprise)
                               .where(Enterprise.email == enterprise_data.email))
    search_ent = result.scalar_one_or_none()
    
    if search_ent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise with this email already exists",
        )
    new_enterprise = Enterprise(
        name=enterprise_data.name,
        email=enterprise_data.email,
        created_by=current_user.id,
    )
    try:
        db.add(new_enterprise)
        await db.flush()
        await db.execute(update(User)
                         .where(User.id == current_user.id)
                         .values(role="admin", enterprise_id=new_enterprise.id))
        await db.commit()
        await db.refresh(new_enterprise)
    except Exception as e:
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

    return new_enterprise


# Enterprise deletion (soft delete only)
@router.delete("/delete/{ent_id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_enterprise(
    ent_id: int, db: db_dependency, current_user: User = Depends(get_current_user)
):

    if cast(int, current_user.enterprise_id) != ent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have administrative authority over this enterprise.",
        )

    result = await db.execute(select(Enterprise).where(Enterprise.id == ent_id))
    enterprise = result.scalar_one_or_none()

    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enterprise not found"
        )
    if enterprise.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise is already inactive",
        )
    try:
        """db.query(Enterprise).filter(Enterprise.id == ent_id).update(
            {"is_active": False}
        )

        db.query(User).filter(User.enterprise_id == ent_id).update(
            {"enterprise_id": None, "role": "user"}
        )"""
        await db.execute(update(User).where(User.id == current_user.id).values({"enterprise_id": None, "role": "user"}))
        await db.execute(update(Enterprise).where(Enterprise.id == current_user.enterprise_id).values(is_active = False))
        await db.commit()
        logger.info(f"Enterprise {ent_id} deleted successfully.")
        return {"message": "Enterprise and memberships cleared."}
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(status_code=500, detail="Database error occurred")

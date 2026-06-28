from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from app.core.db import db_dependency
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger
from app.models.workspace_model import Workspace
from app.models.user_model import User
from app.schemas.workspace_schema import CreateWorkspace, ResponseWorkspace

router = APIRouter(prefix="/v1/workspace", tags=["Workspace"])

logger = get_logger(__name__)


# Create new Workspace
@router.post("/create", response_model=ResponseWorkspace)
async def create_workspace(
    workspace_data: CreateWorkspace,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    # search for email is already exist or not
    result = await db.execute(select(Workspace)
                               .where(Workspace.email == workspace_data.email))
    search_ws = result.scalar_one_or_none()
    
    if search_ws:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace with this email already exists",
        )
    new_workspace = Workspace(
        name=workspace_data.name,
        email=workspace_data.email,
        created_by=current_user.id,
    )
    try:
        db.add(new_workspace)
        await db.flush()
        await db.execute(update(User)
                         .where(User.id == current_user.id)
                         .values(role="admin", workspace_id=new_workspace.id))
        await db.commit()
        await db.refresh(new_workspace)
    except Exception as e:
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

    return new_workspace


# Workspace deletion (soft delete only)
@router.delete("/delete/{workspace_id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_workspace(
    workspace_id: int, db: db_dependency, current_user: User = Depends(get_current_user)
):

    if cast(int, current_user.workspace_id) != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have administrative authority over this workspace.",
        )

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    if workspace.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace is already inactive",
        )
    try:
        await db.execute(update(User).where(User.id == current_user.id).values({"workspace_id": None, "role": "user"}))
        await db.execute(update(Workspace).where(Workspace.id == current_user.workspace_id).values(is_active = False))
        await db.commit()
        logger.info(f"Workspace {workspace_id} deleted successfully.")
        return {"message": "Workspace and memberships cleared."}
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(status_code=500, detail="Database error occurred")

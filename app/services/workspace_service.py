from logging import getLogger

from fastapi import HTTPException, status

from app.core.db import db_dependency
from app.models.workspace_model import Workspace
from app.schemas.workspace_schema import CreateWorkspace

logger = getLogger(__name__)


async def add_workspace(
    workspace_data: CreateWorkspace, user_id: int, db: db_dependency
):

    new_workspace = Workspace(
        name=workspace_data.name, email=workspace_data.email, created_by=user_id
    )

    try:
        db.add(new_workspace)
        await db.commit()
        await db.refresh(new_workspace)
    except Exception as e:
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

    return new_workspace

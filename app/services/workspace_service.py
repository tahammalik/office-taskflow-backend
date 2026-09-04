from logging import getLogger
from fastapi import HTTPException, status
from app.core.db import db_dependency
from app.schemas.workspace_schema import CreateWorkspace

logger = getLogger(__name__)

class WorkspaceService:
   def __init__(self):
      pass

   async def create_workspace(
           self,
           workspace_data: CreateWorkspace,
           user_id: int,
           db: db_dependency
   ) -> Workspace:
      new_workspace = Workspace(
         name=workspace_data.name,
         email=workspace_data.email,
         created_by=user_id
      )

      try:
         db.add(new_workspace)
         await db.commit()
         await db.refresh(new_workspace)
      except Exception as e:
         await db.rollback()
         logger.error("DB ERROR: %s", e)
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
         )

      return new_workspace

   async def delete_workspace(self, workspace_id: int, db:db_dependency) -> Workspace:
      if current_user.workspace_id != workspace_id:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have access over this workspace.",
         )

      workspace = await db.scalar(
         select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.created_by == current_user.id
         )
      )

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
         await db.execute(update(Workspace)
                          .where(Workspace.id == workspace_id)
                          .values(is_active=False)
                          )
         await db.execute(update(User)
                          .where(User.workspace_id == workspace_id)
                          .values({"workspace_id": None, "role": "user"})
                          )
         await db.execute(update(Project)
                          .where(Project.workspace_id == workspace_id)
                          .values(is_deleted=True)
                          )
         await db.execute(update(Task)
                          .where(Task.workspace_id == workspace_id)
                          .values(is_deleted=True)
                          )
         await db.execute(update(Team)
                          .where(Team.workspace_id == workspace_id)
                          .values(is_deleted=True)
                          )
         await db.commit()
         logger.info(f"Workspace {workspace_id} deleted successfully.")

      except Exception as e:
         await db.rollback()
         logger.error("DB ERROR: %s", e)
         raise HTTPException(status_code=500, detail="Database error occurred")
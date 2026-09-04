from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from app.core.db import db_dependency
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger
from app.models.workspace_model import Workspace
from app.models.project_model import Project
from app.models.invitation_model import Invitation
from app.models.team_model import Team
from app.models.task_model import Task
from app.models.user_model import User
from app.schemas.workspace_schema import CreateWorkspace, ResponseWorkspace
from app.schemas.invitation_schema import CreateInvitation,AcceptInvitation,ResponseInvitation
from typing import Annotated
from app.core.config import SecretConfig
from app.services.email_services import send_invite_email
from app.services.workspace_service import WorkspaceService
from datetime import datetime, timezone

router = APIRouter(prefix="/v1/workspace", tags=["Workspace"])
settings = SecretConfig()
logger = get_logger(__name__)
workspaceservice = WorkspaceService()

# Create new Workspace
@router.post(
        "/create",
        response_model=ResponseWorkspace,
        status_code=status.HTTP_201_CREATED,
    )
async def create(
    workspace_data: CreateWorkspace,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    return await workspaceservice.create_workspace(
        workspace_data=workspace_data,
        user_id=current_user.id,
        db=db_dependency,
    )

# Workspace deletion (soft delete only)
@router.delete("/delete", dependencies=[Depends(require_role(["admin"]))],status_code=204)
async def delete_workspace(
    workspace_id: int, db: db_dependency,
    current_user: User = Depends(get_current_user)
):

    return await workspaceservice.delete(
        workspace_id=workspace_id,
        db=db_dependency
    )


@router.get("/current", response_model=ResponseWorkspace)
async def list_workspaces(db: db_dependency,current_user: User = Depends(get_current_user)):
    try:
        workspace = await db.scalar(
            select(Workspace).where(
                Workspace.id == current_user.workspace_id,
                Workspace.is_active == True
            ).options(
                selectinload(Workspace.teams).selectinload(Team.leader),
                selectinload(Workspace.teams).selectinload(Team.members),
                selectinload(Workspace.projects).selectinload(Project.teams),
                selectinload(Workspace.projects).selectinload(Project.initiator),
                selectinload(Workspace.users)
            )
        )
        
        if not workspace:
           raise HTTPException(
               status_code=404,
               detail="Workspace did not found!"
           )
        return workspace
    except Exception as e:
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
# create invitation for user to join workspace
@router.post('/invite',response_model=ResponseInvitation,dependencies=[Depends(require_role(["admin","manager"]))],status_code=201)
async def invite_user(invite:CreateInvitation,current_user:Annotated[User,Depends(get_current_user)],db:db_dependency):

    workspace = await db.scalar(
        select(Workspace).where(
            Workspace.id == current_user.workspace_id,
            Workspace.is_active == True
        )
    )
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    existing_invite = await db.scalar(
        select(Invitation).where(
            Invitation.email == invite.email,
            Invitation.status == "pending"
        )
    )

    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An invitation for this user already exists"
        )
    # generate a unique token for the invitation
    token = Invitation.generate_token()
    # First add invitation to the database
    # Then send an email to the invited user with a link to accept the invitation
    new_invitation = Invitation(
                email=invite.email,
                role=invite.role,
                workspace_id=current_user.workspace_id,
                invited_by=current_user.id,
                token=token,
                status="pending",
                expires_at=Invitation.default_expiry()
            )
    try:
        db.add(new_invitation)
        await db.commit()
        await db.refresh(new_invitation)
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
    

    await send_invite_email(
                receiver_email=invite.email,
                token=token,
                workspace_name=workspace.name
            )

    return ResponseInvitation(**new_invitation.__dict__)

# Accept invitation for user to join workspace. who is not registered yet.
@router.get('/invitetions/accept?token={token}',status_code=200)
async def get_invitation(token:str,db:db_dependency):
    invitation = await db.scalar(
        select(Invitation).where(
            Invitation.token == token
        )
    )

    if not invitation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    if invitation.status != "pending":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invitation is no longer valid")
    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invitation has expired")

    existing_user = await db.scalar(select(User).where(User.email == invitation.email))

    if existing_user:
        return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/login?invite_token={token}")
    else:
        return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/signup?invite_token={token}&email={invitation.email}")
# Accept invitation for user to join workspace. who is already registered and logged in.
@router.post('/invitation/accept',response_model=ResponseWorkspace,status_code=200)
async def accept_invitation(invite:AcceptInvitation,db:db_dependency,current_user:Annotated[User,Depends(get_current_user)]): 
    invitation = await db.scalar(
        select(Invitation).where(
            Invitation.token == invite.token
        )
    )

    if not invitation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    if invitation.status != "pending":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invitation is no longer valid")
    if invitation.expires_at <= datetime.now(timezone.utc):
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invitation has expired")
    if invitation.email != current_user.email:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This invitation was not issued to your account")
    try:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(role=invitation.role, workspace_id=invitation.workspace_id)
        )
        invitation.status = "accepted"
        await db.commit()

        workspace = await db.scalar(select(Workspace).where(Workspace.id == invitation.workspace_id))
        await db.refresh(workspace, attribute_names=["projects", "teams", "users"])
        return workspace
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")

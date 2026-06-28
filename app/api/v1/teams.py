import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from app.core.db import db_dependency
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger
from app.models.user_model import User
from app.models.team_model import Team
from app.schemas.project_schema import ProjectResponse
from app.schemas.team_schema import CreateTeam, TeamResponse

router = APIRouter(prefix="/v1/teams", tags=["Teams"])

logger = get_logger(__name__)


# create team endpoint role required admin
@router.post(
    "/create",
    response_model=TeamResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
async def add_new_team(
    group_data: CreateTeam,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    new_team = Team(
        team_name=group_data.team_name,
        description=group_data.description,
        workspace_id=current_user.workspace_id,
        leader_id=current_user.id,
    )
    try:
        db.add(new_team)
        await db.commit()
        await db.refresh(new_team)
        logger.info(f"team created : {group_data.team_name}")
        return new_team
    except Exception as e:
        await db.rollback()
        logger.error(f"DB ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


# show all teams according to users workspace id
@router.get(
    "/show",
    response_model=List[TeamResponse],
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
async def show_teams(db: db_dependency, current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Team).where(Team.workspace_id == current_user.workspace_id)
    )
    teams = result.scalars().all()
    if not teams:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teams not found"
        )
    return teams


# delete team endpoint only admin can access this endpoint
@router.delete("/delete/{team_id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_team(
    team_id: int, db: db_dependency, current_user: User = Depends(get_current_user)
):
    team_result = await db.execute(
        select(Team).where(
            Team.id == team_id, Team.workspace_id == current_user.workspace_id
        )
    )
    team = team_result.scalars().first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    try:
        await db.execute(
            update(Team)
            .where(Team.id == team_id, Team.workspace_id == current_user.workspace_id)
            .values({"is_active": False, "is_deleted": True})
        )
        await db.commit()
        logger.info(f"team deleted : {team.team_name}")
        return {"message": "Team deleted successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"DB ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# show projects assigned to a team endpoint only team members can access this endpoint
@router.get("/{team_id}/assigned-projects", response_model=List[ProjectResponse],dependencies=[Depends(require_role(["admin","manager","user"]))])
async def show_projects(
    team_id: int, db: db_dependency, current_user: User = Depends(get_current_user)
):
    user_result = await db.execute(
        select(User).where(
            User.id == current_user.id, User.workspace_id == current_user.workspace_id
        )
    )
    user = user_result.scalars().first()
    team_result = await db.execute(
        select(Team).where(
            Team.id == team_id, Team.workspace_id == current_user.workspace_id
        )
    )
    team = team_result.scalars().first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    if current_user.role == "user" and current_user.id != team.leader_id and team_id not in user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this team's projects.",
        )

    # Check if user is in the team (either leader or has a task in the team, simplified check)
    # For now, just allow if they are in the same workspace
    return team.projects

# Assign user to team endpoint only admin and team leader/manager can access this endpoint
@router.post("/{user_id}/{team_id}/assign",dependencies=[Depends(require_role(["admin","manager"]))])
async def assign_user_to_team(user_id: int, team_id: int, db: db_dependency, current_user: User = Depends(get_current_user)):
    
    result_team = await db.execute(select(Team).where(
        Team.id == team_id,
        Team.workspace_id == current_user.workspace_id
    ))

    team = result_team.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!"
        )
    if current_user.id != team.leader_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to assign users to this team."
        )

    assign_user = await db.execute(select(User).where(
        User.workspace_id == current_user.workspace_id,
        User.id == user_id
    ))
    user = assign_user.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
    if user.team_id and user.team_id == team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this team."
        )
    
    team.members.append(user_id)
    user.team_id.append(team_id)
    await db.commit()
    return {"message": "User assigned to team successfully"}
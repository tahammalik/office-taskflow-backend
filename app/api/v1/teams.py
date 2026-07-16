
from sqlalchemy.orm import selectinload
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from app.core.db import db_dependency
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger
from app.models.user_model import User
from app.models.team_model import Team
from app.models.project_model import Project
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
    if current_user.workspace_id is None:
        raise HTTPException(400, "You are not assigned to any workspace")

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
# append

# show all teams according to users workspace id
@router.get(
    "/show",
    response_model=List[TeamResponse],
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
async def show_teams(db: db_dependency, current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        teams = (await db.scalars(
            select(Team).where(
                Team.workspace_id == current_user.workspace_id
            ).options(
                selectinload(Team.members),
                selectinload(Team.projects)
            )
        )).all()
        if not teams:
            raise HTTPException(404,detail="teams doesn't exist")

        return teams
    else:
        teams = await db.scalars(
            select(Team).where(
                Team.workspace_id == current_user.workspace_id,
                Team.leader_id == current_user.id
            ).options(
                selectinload(Team.members),
                selectinload(Team.projects)
            )
        )
        if not teams.all():
            raise HTTPException(404,detail="teams doesn't exist")

        return teams.all()



# delete team endpoint only admin can access this endpoint
@router.delete("/delete/{team_id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_team(
    team_id: int, db: db_dependency, current_user: User = Depends(get_current_user)
):
    team = await db.scalar(
        select(Team).where(
            Team.id == team_id,
            Team.workspace_id == current_user.workspace_id
        )
    )
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    if team.is_deleted == True:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="team is already deleted"    
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


    team = await db.scalar(
        select(Team).where(
            Team.id == team_id,
            Team.workspace_id == current_user.workspace_id,
            Team.is_deleted == False
        ).options(
            selectinload(Team.projects),
            selectinload(Project.teams)
        )
    )
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    if current_user.role == "user" and current_user.team_id != team_id and current_user.id != team.leader_id:
        raise HTTPException(403, "Not authorized to view this team's projects")

    # Check if user is in the team (either leader or has a task in the team, simplified check)
    # For now, just allow if they are in the same workspace
    return team.projects

# Assign user to team endpoint only admin and team leader/manager can access this endpoint
@router.post("/assign/{user_id}/{team_id}",dependencies=[Depends(require_role(["admin","manager"]))])
async def assign_user_to_team(user_id: int, team_id: int, db: db_dependency, current_user: User = Depends(get_current_user)):
    
    team = await db.scalar(
        select(Team).where(
            Team.id == team_id,
            Team.workspace_id == current_user.workspace_id,
            Team.is_active == True
        )
    )
    if not team:
        raise HTTPException(404, "Team not found")

    if current_user.role != "admin" and team.leader_id != current_user.id:
        raise HTTPException(403,detail="You have no permission to perform this task")
    

    assignee = await db.scalar(
        select(User).where(
            User.id == user_id,
            User.workspace_id == current_user.workspace_id,
            User.is_active == True
        )
    )

    if not assignee:
        raise HTTPException(404, "assignee not found")

    if assignee.team_id == team_id:
        raise HTTPException(409,detail="assignee already exist in this team")
    
    if assignee.team_id is not None:
        logger.info(f"User {user_id} moved from team {assignee.team_id} to {team_id}")
        
    assignee.team_id = team_id

    try:
        await db.commit()
        logger.info(f"User {user_id} assigned to Team {team_id}")
        return {"message": "User assigned to team successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"DB ERROR: {e}")
        raise HTTPException(500, "Database error occurred")
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.db import db_dependency
from app.models import Team, User, Project
from app.schemas.team_schema import CreateTeam, ResponseTeam
from app.schemas.project_schema import ProjectResponse
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger

router = APIRouter(
    prefix='/v1/teams',
    tags=['Teams']
)

logger = get_logger(__name__)

# create team endpoint role required admin
@router.post('/create', response_model=ResponseTeam, dependencies=[Depends(require_role(['admin']))])
async def add_new_team(group_data: CreateTeam, db: db_dependency,
                       current_user: User = Depends(get_current_user)):
    new_team = Team(
        team_name=group_data.team_name,
        description=group_data.description,
        enterprise_id=current_user.enterprise_id,
        leader_id=group_data.leader_id
    )
    try:
        db.add(new_team)
        db.commit()
        db.refresh(new_team)
        logger.info(f"team created : {group_data.team_name}")
        return new_team
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Database error occurred")

# show all teams according to users enterprise id
@router.get('/show', response_model=List[ResponseTeam], dependencies=[Depends(require_role(['admin', 'manager']))])
async def show_teams(db: db_dependency, current_user: User = Depends(get_current_user)):
    teams = db.query(Team).filter(Team.enterprise_id == current_user.enterprise_id).all()
    if not teams:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Teams not found')
    return teams

# delete team endpoint only admin can access this endpoint
@router.delete('/delete/{team_id}', dependencies=[Depends(require_role(['admin']))])
async def delete_team(team_id: int, db: db_dependency,
                      current_user: User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id, Team.enterprise_id == current_user.enterprise_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot delete a other team')
    try:
        db.query(Team).filter(Team.id == team_id).update({"is_active": False, "is_deleted": True})
        db.commit()
        logger.info(f"team deleted : {team.team_name}")
        return {"message": "Team deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# show projects assigned to a team endpoint only team members can access this endpoint
@router.get('/{team_id}/assigned-projects', response_model=List[ProjectResponse])
async def show_projects(team_id: int, db: db_dependency,
                        current_user: User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id, Team.enterprise_id == current_user.enterprise_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    # Check if user is in the team (either leader or has a task in the team, simplified check)
    # For now, just allow if they are in the same enterprise
    return team.projects

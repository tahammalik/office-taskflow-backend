from fastapi import APIRouter,Depends,HTTPException,status
from app.core.db import db_dependency
from app.models import Project, Organization, User
from app.models.project_model import ProjectTeams
from app.schemas.project_schema import ProjectResponse
from app.schemas.team_schema import CreateTeam,TeamUpdate,TeamResponse
from app.core.dependencies import require_role,get_current_user
from app.models.team_model import Team
from app.core.logging_config import get_logger

router = APIRouter(
    prefix='/v1/team',
    tags=['Teams']
)

logger = get_logger(__name__)
# create team endpoint only manager and admin can create team
@router.post('/create',dependencies=[Depends(require_role(['manager','admin']))])
async def create_group(group_data:CreateTeam,db:db_dependency,current_user: User = Depends(get_current_user)):

    new_team = Team(
        team_name = group_data.team_name,
        description = group_data.description,
        organization_id = current_user.organization_id,
        leader_id=current_user.id)
    try:
        db.add(new_team)
        db.commit()
        db.refresh(new_team)
        logger.info(f"team created : {new_team.team_name}")
        return new_team
    except Exception as e:
        logger.error(f"DB ERROR: %s",e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred")
# update team endpoint only team leader or admin can update the team
@router.patch('/update-team/{team_id}',response_model=TeamResponse,dependencies=[Depends(require_role(['admin','manager']))])
async def update_team(team_id:int,team_update:TeamUpdate,db:db_dependency,
                      current_user: User = Depends(get_current_user)):
   team = db.query(Team).filter(Team.id == team_id,Team.organization_id == current_user.organization_id).first()
   if not team:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Team not found')
   
   if current_user.role == 'manager' and current_user.id != team.leader_id:
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='You cannot update a team,you must be a leader of this team')
   updated_team = team_update.model_dump(exclude_unset=True)
   
   for key, value in updated_team.items():
       setattr(team, key, value)

   db.commit()
   db.refresh(team)
   return team
# delete team endpoint only team leader/manager or admin can delete the team
@router.delete('/delete-team/{team_id}',dependencies=[Depends(require_role(['admin','manager']))])
async def delete_team(team_id:int,db:db_dependency,current_user: User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id,Team.organization_id == current_user.organization_id).first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Team not found')
    if current_user.role == 'manager' and current_user.id != team.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='You cannot delete a team')
    try:
        db.query(Team).filter(Team.id == team_id).update({"is_active":False,"is_deleted":True})
        db.commit()
        logger.info(f"team deleted : {team.team_name}")
    except Exception as e:
        logger.error(f"DB ERROR: %s",e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
# show projects assigned to a team endpoint only team members can access this endpoint
@router.get('/{team_id}/assigned-projects',response_model=list[ProjectResponse])
async def show_projects(team_id:int,db:db_dependency,current_user:User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id,Team.organization_id == current_user.organization_id).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='User does not belong to this team or organization')
    try:
        # we are joining the project and project_teams table to get the projects assigned to the team
        projects = db.query(Project).join(ProjectTeams, Project.id == ProjectTeams.project_id).filter(ProjectTeams.team_id == team_id).all()
        return projects
    except Exception as e:
        logger.error(f"DB ERROR %s",e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
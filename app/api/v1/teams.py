from fastapi import APIRouter,Depends,HTTPException,status
from app.core.db import db_dependency
from app.models import Project, Organization, User
from app.schemas.project_schema import ProjectResponse
from app.schemas.team_schema import CreateTeam,TeamUpdate
from app.core.dependencies import require_role,get_current_user
from app.models.team_model import Team
from app.core.logging_config import get_logger

router = APIRouter(
    prefix='/v1/team',
    tags=['Teams']
)

logger = get_logger(__name__)

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
# update team
@router.patch('/update-team',dependencies=[Depends(require_role(['admin','manager']))])
async def update_team(id:int,team_update:TeamUpdate,db:db_dependency,current_user: User = Depends(get_current_user)):
    user_team = db.query(User).filter(User.team_id == current_user.team_id).first()
    team = db.query(Team).filter(Team.id == id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Team not found')
    update_team = team_update.model_dump(exclude_unset=True)
    for key,val in update_team.items():
        setattr(team,key,val)
# soft delete of team
@router.delete('/delete-team/{team_id}',dependencies=[Depends(require_role(['admin','manager']))])
async def delete_team(team_id:int,db:db_dependency,current_user: User = Depends(get_current_user)):
    user = db.query(Team).filter(Team.organization_id == current_user.organization_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Organization not found')
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='team not found')
    team.is_active = False
    try:
        db.commit()
        logger.info("fTeam {id} soft-deleted (deactivated)")
    except Exception as e:
        logger.error(f"DB ERROR %s",e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# show team projects
@router.get('/{team_id}/assigned-projects',response_model=list[ProjectResponse])
async def show_projects(team_id:int,db:db_dependency,current_user:User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == current_user.team_id,Team.organization_id == current_user.organization_id).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='User does not belong to this team or organization')
    try:
        projects = db.query(Project).all()
        return projects
    except Exception as e:
        logger.error(f"DB ERROR %s",e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
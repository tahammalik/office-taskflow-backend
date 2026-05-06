from fastapi import APIRouter,HTTPException,status,Depends
from app.schemas.project_schema import ProjectResponse,CreateProject
from app.core.dependencies import require_role,get_current_user
from app.core.db import db_dependency
from app.models import team_model, organization_model, user_model, Organization
from app.models.project_model import ProjectTeams,Project
from app.core.logging_config import get_logger


router = APIRouter(
    prefix='/v1/projects',
    tags=['Projects']
)

logger = get_logger(__name__)

# create project endpoint role required admin or manager
@router.post('/create',response_model=ProjectResponse,dependencies=[Depends(require_role(['admin','manager']))])
async def create_projects(project_data:CreateProject,db:db_dependency,current_user: user_model.User = Depends(get_current_user)):

    new_project = Project(
        title = project_data.title,
        description = project_data.description,
        dead_line = project_data.dead_line,
        created_by = current_user.id,
        organization_id = current_user.organization_id)
    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        logger.info(f'project created: {new_project.id}')
        return new_project
    except Exception as e:
        db.rollback()
        logger.error(f'DB ERROR: %s',e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="db error occurred")

# show all projects according to users organization id
@router.get('/show',response_model=list[ProjectResponse],dependencies=[Depends(require_role(['admin','manager']))])
async def show_projects(db:db_dependency,current_user: user_model.User = Depends(get_current_user)):

    projects = db.query(Project).filter(Project.organization_id == current_user.organization_id).all()
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="projects not found")
    return projects

@router.delete('/delete',dependencies=[Depends(require_role(['admin','manager']))])
async def delete_project(project_id:int,db:db_dependency,current_user: user_model.User = Depends(get_current_user)):

    project = db.query(Project).filter(Project.id == project_id,
                                       Project.organization_id == current_user.organization_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='project not found or  you do not have access to it')
    try:
        db.delete(project)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f'DB ERROR: %s',e)
        raise HTTPException(
                status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='db error occurred')

# assign project to team endpoint role required admin or manager
@router.post('/assign-project/{project_id}/to-team/{team_id}',dependencies=[Depends(require_role(['manager','admin']))])
async def assign_project(project_id:int,team_id:int,db:db_dependency,current_user: user_model.User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id,Project.organization_id == current_user.organization_id).first()
    team = db.query(team_model.Team).filter(team_model.Team.id == team_id,team_model.Team.organization_id == current_user.organization_id).first()
    if not project or not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='project or team not found or you do not have access to them')
    if project.organization_id != team.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='project and team do not belong to the same organization')
    try:
       assigned_project = ProjectTeams(project_id=project_id,team_id=team_id)
       db.add(assigned_project)
       db.commit()
       db.refresh(assigned_project)
       logger.info(f"Project assigned : {project_id} to Team:{team_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s",e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

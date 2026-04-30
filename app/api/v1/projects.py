from fastapi import APIRouter,HTTPException,status,Depends
from app.schemas.project_schema import ProjectResponse,CreateProject
from app.core.dependencies import require_role,get_current_user
from app.core.db import db_dependency
from app.models import team_model, organization_model, user_model
from app.models.project_model import ProjectTeams,Project
from app.core.logging_config import get_logger
from app.services.user_service import user_to_response

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
    if projects is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="projects not found")
    return projects

@router.delete('/delete',dependencies=[Depends(require_role(['admin','manager']))])
async def delete_project(project_id:int,db:db_dependency,current_user: user_model.User = Depends(get_current_user)):

    organization = db.query(organization_model.Organization).filter(organization_model.Organization.id == current_user.organization_id).first()
    # verify that user and organization is related or not
    # if not raise error
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='user and organization not related to each other')
    # if yes then delete project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Project not found!')
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
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Project not found')
    
    team = db.query(team_model.Team).filter(team_model.Team.id == team_id).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Team not found')
    try:
       assigned_project = ProjectTeams(project_id=project_id,team_id=team_id)
       db.add(assigned_project)
       db.commit()
       db.refresh(assigned_project)
       logger.info(f"Project assigned : {project_id} to Team: {team.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"DB ERROR: %s",e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

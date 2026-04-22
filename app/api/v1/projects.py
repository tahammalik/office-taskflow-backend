from fastapi import APIRouter,HTTPException,status,Depends
from app.schemas.project_schema import ProjectResponse,CreateProject
from app.core.dependencies import require_role,get_current_user
from app.core.db import db_dependency
from app.models import Project,User
from logging import getLogger
from app.services.user_service import user_to_response

router = APIRouter(
    prefix='/projects/v1',
    tags=['Projects']
)

logger = getLogger(__name__)

@router.post('/create',response_model=ProjectResponse,dependencies=[Depends(require_role(['admin','manager']))])
async def create_projects(project_data:CreateProject,db:db_dependency,current_user: User = Depends(get_current_user)):

    new_project = Project(
        title = project_data.title,
        description = project_data.description,
        dead_line = project_data.dead_line,
        created_by = current_user.id,
        organization_id = current_user.organization_id
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return new_project
    except Exception as e:
        db.rollback()
        logger.error(f'DB ERROR: %s',e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="db error ocurred"
        )
    
    

@router.get('/show/',response_model=ProjectResponse,dependencies=[Depends(require_role(['admin','manager']))])
def show_projects(db:db_dependency,current_user: User = Depends(get_current_user)):

    projects = db.query(Project).filter(Project.organization_id == current_user.organization_id).all()

    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="projects not found"
        )
    return projects
    


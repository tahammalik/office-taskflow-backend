from typing import cast
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert,select
from app.core.exceptions import *
from sqlalchemy.exc import IntegrityError
from app.core.db import db_dependency
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger
from app.models import team_model, user_model
from app.models.project_model import Project, ProjectTeams
from app.schemas.project_schema import CreateProject, ProjectResponse

router = APIRouter(prefix="/v1/projects", tags=["Projects"])

logger = get_logger(__name__)


# create project endpoint role required admin or manager
@router.post(
    "/create",
    response_model=ProjectResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
async def create_projects(
    project_data: CreateProject,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):

    new_project = Project(
        title=project_data.title,
        description=project_data.description,
        deadline=project_data.deadline,
        created_by=current_user.id,
        workspace_id=current_user.workspace_id,
    )
    try:
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        logger.info(f"project created: {new_project.id}")
        project = await db.get(Project,new_project.id)
        return project
    
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="db error occurred",
        )

@router.patch(
        "/update/{project_id}",
        response_model=ProjectResponse,
        dependencies=[Depends(require_role(["admin", "manager"]))]
)
async def update_project(project_id:int,db:db_dependency):
    pass

# show all projects according to users workspace id
@router.get(
    "/show",
    response_model=list[ProjectResponse],
    dependencies=[Depends(require_role(["admin", "manager"]))],
    status_code=200
)
async def show_projects(
    db: db_dependency, current_user: user_model.User = Depends(get_current_user)
):

    result = await db.execute(select(Project).where(
        Project.workspace_id == current_user.workspace_id
        ))
    projects = result.scalars().all()

    return projects


@router.delete("/delete/{project_id}", dependencies=[Depends(require_role(["admin", "manager"]))])
async def delete_project(
    project_id: int,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):
    if current_user.role == "admin":
        project = await db.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.workspace_id == current_user.workspace_id
            )
        )
    project = await db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.created_by == current_user.id,
            Project.workspace_id == current_user.workspace_id
        )
    )
    
    if not project:
        raise HTTPException(404,detail="Project not found")

    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(403,detail="You have no permission to delete this project")

    try:
        await db.delete(project)
        await db.commit()
        logger.info(f"Project {project.id} deleted by user {current_user.id}")
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="db error occurred",
        )


# assign project to team endpoint. role required admin or manager
@router.post(
    "/assign/{project_id}/{team_id}",
    dependencies=[Depends(require_role(["manager", "admin"]))],
    response_model=ProjectResponse
)
async def assign_project(
    project_id: int,
    team_id: int,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):
    project = await db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == current_user.workspace_id
        )
    )

    team = await db.scalar(
        select(team_model.Team).where(
            team_model.Team.id == team_id,
            team_model.Team.workspace_id == current_user.workspace_id
        )
    )

    if not project or not team:       
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="project or team not found or you do not have access to them",
        )
    if project.workspace_id != team.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="project and team do not belong to the same workspace",
        )
    try:
        await db.execute(insert(ProjectTeams).values(project_id=project_id,team_id=team_id))
        await db.commit()

        project = await db.get(Project,project_id)
        logger.info(f"Project {project_id} assigned to Team:{team_id}")
        return project
    
    except IntegrityError:
        await db.rollback()

        existing = await db.scalar(
            select(ProjectTeams).where(ProjectTeams.c.project_id == project_id,
                ProjectTeams.c.team_id == team_id
            )
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project already assigned to this team"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid project or team reference"
            )
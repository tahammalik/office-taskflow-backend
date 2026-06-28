from typing import cast
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert,select
from app.core.exceptions import *
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
        return new_project
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="db error occurred",
        )


# show all projects according to users workspace id
@router.get(
    "/show",
    response_model=list[ProjectResponse],
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
async def show_projects(
    db: db_dependency, current_user: user_model.User = Depends(get_current_user)
):

    result = await db.execute(select(Project).where(
        Project.workspace_id == current_user.workspace_id
        ))
    projects = result.scalars().all()
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="projects not found"
        )
    return projects


@router.delete("/delete/{project_id}", dependencies=[Depends(require_role(["admin", "manager"]))])
async def delete_project(
    project_id: int,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):

    result = await db.execute(select(Project).where(
        Project.id == project_id,
        Project.workspace_id == current_user.workspace_id,
    ))

    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="project not found or  you do not have access to it",
        )

    if current_user.role != "admin" and project.created_by != current_user.id:
        raise ForbiddenError("You do not have permission to delete this project.")

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
)
async def assign_project(
    project_id: int,
    team_id: int,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):
    project_result = await db.execute(select(Project).where(
        Project.id == project_id,
        Project.workspace_id == current_user.workspace_id
    ))

    project = project_result.scalar_one_or_none()
    
    team_result = await db.execute(select(team_model.Team).where(
        team_model.Team.id == team_id,
        team_model.Team.workspace_id == current_user.workspace_id
    ))

    team = team_result.scalar_one_or_none()

    if not project or not team:             # verify team or project exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="project or team not found or you do not have access to them",
        )
    if cast(int, project.workspace_id) != cast(int, team.workspace_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="project and team do not belong to the same workspace",
        )
    try:
        assigned_project = await db.execute(insert(ProjectTeams)
                                            .values(project_id=project_id,team_id=team_id))
        
        await db.commit()
        logger.info(f"Project {project_id} assigned to Team:{team_id}")
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

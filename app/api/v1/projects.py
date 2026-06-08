from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert

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
        dead_line=project_data.dead_line,
        created_by=current_user.id,
        enterprise_id=current_user.enterprise_id,
    )
    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        logger.info(f"project created: {new_project.id}")
        return new_project
    except Exception as e:
        db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="db error occurred",
        )


# show all projects according to users enterprise id
@router.get(
    "/show",
    response_model=list[ProjectResponse],
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
async def show_projects(
    db: db_dependency, current_user: user_model.User = Depends(get_current_user)
):

    projects = (
        db.query(Project)
        .filter(Project.enterprise_id == current_user.enterprise_id)
        .all()
    )
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="projects not found"
        )
    return projects


@router.delete("/delete", dependencies=[Depends(require_role(["admin", "manager"]))])
async def delete_project(
    project_id: int,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.enterprise_id == current_user.enterprise_id,
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="project not found or  you do not have access to it",
        )
    try:
        db.delete(project)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="db error occurred",
        )


# assign project to team endpoint role required admin or manager
@router.post(
    "/assign-project/{project_id}/{team_id}",
    dependencies=[Depends(require_role(["manager", "admin"]))],
)
async def assign_project(
    project_id: int,
    team_id: int,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.enterprise_id == current_user.enterprise_id,
        )
        .first()
    )
    team = (
        db.query(team_model.Team)
        .filter(
            team_model.Team.id == team_id,
            team_model.Team.enterprise_id == current_user.enterprise_id,
        )
        .first()
    )
    if not project or not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="project or team not found or you do not have access to them",
        )
    if cast(int, project.enterprise_id) != cast(int, team.enterprise_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="project and team do not belong to the same enterprise",
        )
    try:
        assigned_project = insert(ProjectTeams).values(
            project_id=project_id, team_id=team_id
        )
        db.add(assigned_project)
        db.commit()
        db.refresh(assigned_project)
        logger.info(f"Project assigned : {project_id} to Team:{team_id}")
    except Exception as e:
        db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

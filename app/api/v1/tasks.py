"""
this file maintains request of tasks
"""
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, cast,Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.db import db_dependency
from app.core.dependencies import get_current_user, require_role
from app.core.logging_config import get_logger
from app.models import task_model, team_model, user_model, workspace_model,taskhistory_model
from app.schemas.task_schema import CreateTask, ResponseTask,TaskUpdate

router = APIRouter(prefix="/v1/task", tags=["Tasks"])

logger = get_logger(__name__)


# manager/admin can create task
@router.post(
    "/create",
    dependencies=[Depends(require_role(["admin", "manager"]))],
    response_model=ResponseTask,
)
async def add_new_task(
    task_data: CreateTask,
    db: db_dependency,
    current_user: user_model.User = Depends(get_current_user),
):
    # verify the team belongs to current user workspace
    team = await db.scalar(
        select(team_model.Team).where(
            team_model.Team.id == task_data.team_id,
            team_model.Team.workspace_id == current_user.workspace_id,
            team_model.Team.is_active == True
        )
    )
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found or not in your workspace",
        )
    # manager only create task for there team
    if current_user.role == "manager" and current_user.id != team.leader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not leader"
        )
    # verify the assign user belongs to same workspace
    assigned_user = await db.scalar(
        select(user_model.User).where(
            user_model.User.id == task_data.assign_to,
            user_model.User.workspace_id == current_user.workspace_id,
            user_model.User.team_id == task_data.team_id,
            user_model.User.is_active == True
        )
    )

    if not assigned_user:  # its ensure that assigned_user is None or not
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="assigned user not found."
        )

    new_task = task_model.Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        dead_line=task_data.dead_line,
        team_id=task_data.team_id,
        assign_to=task_data.assign_to,
        created_by=current_user.id,
        workspace_id = current_user.workspace_id
    )

    try:
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        logger.info(f"task created with title:{task_data.title}.")
        task = await db.scalar(
            select(task_model.Task)
            .where(task_model.Task.id == new_task.id)
            .options(
                selectinload(task_model.Task.assigned_employee),
                selectinload(task_model.Task.creator_manager)
            )
        )
        return task
    except Exception as e:
        logger.error(f"Database connection error! {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

@router.patch("/update/{task_id}",response_model=ResponseTask) # update task status
async def update_task_status(task_id:int,
                             task_data:TaskUpdate,
                             db: db_dependency,
                             current_user: Annotated[user_model.User,Depends(get_current_user)]
):
    if current_user.role == "admin":
        task = await db.scalar(
        select(task_model.Task).where(
            task_model.Task.id == task_id,
            task_model.Task.workspace_id == current_user.workspace_id
        )
    )
    elif current_user.role == "manager":
        task = await db.scalar(
        select(task_model.Task)
        .join(team_model.Team, team_model.Team.id == task_model.Task.team_id)
        .where(
            task_model.Task.id == task_id,
            task_model.Task.workspace_id == current_user.workspace_id,
            team_model.Team.leader_id == current_user.id
        )
    )
    else:
        task = await db.scalar(
            select(task_model.Task).where(
                task_model.Task.id == task_id,
                task_model.Task.team_id == current_user.team_id,
                task_model.Task.workspace_id == current_user.workspace_id
            )
        )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not in your workspace",
        )
    if current_user.role == "user" and current_user.id != task.assign_to:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own task",
        )
    update_data = task_data.model_dump(exclude_none=True)
    update_data.pop("status_comment",None)
    if not update_data and not task_data.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update"
        )
    if current_user.role == "user":
        not_allowed = set(update_data.keys()) - {"status"}
        if not_allowed:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"Employees can only update status. Not allowed: {not_allowed}",
            )
    if "status" in update_data:
        history = taskhistory_model.TaskHistory(
            task_id=task.id,
            changed_by=current_user.id,
            old_status=task.status,
            new_status=update_data["status"],
            comment=task_data.status_comment
        )
        db.add(history)
    for key,value in update_data.items():
        setattr(task, key, value)
    try:
        await db.commit()
        await db.refresh(task)
        logger.info(f"Task {task_id} updated by user {current_user.id}")
        return task
    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

# only employee can see their own task
@router.get("/show", response_model=List[ResponseTask])
async def get_my_tasks(
    db: db_dependency, current_user: user_model.User = Depends(get_current_user)
):
    try:
        tasks = (await db.scalars(
            select(task_model.Task)
            .where(task_model.Task.assign_to == current_user.id)
            .options(
                selectinload(task_model.Task.assigned_employee),
                selectinload(task_model.Task.creator_manager)
            )
        )).all()
        
        return tasks

    except Exception as e:
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

@router.get("/progress", dependencies=[Depends(require_role(["manager", "admin"]))], response_model=List[ResponseTask])
async def see_progress(
    db: db_dependency,
    current_user: Annotated[user_model.User,Depends(get_current_user)]
):
    try:
        if current_user.role == "admin":
            # Admin sees ALL tasks in the workspace
            query = select(task_model.Task).where(
                task_model.Task.workspace_id == current_user.workspace_id
            )
        else:
            # Manager sees only tasks from teams they lead
            query = (
                select(task_model.Task)
                .join(team_model.Team, team_model.Team.id == task_model.Task.team_id)
                .where(
                    team_model.Team.leader_id == current_user.id,
                    team_model.Team.workspace_id == current_user.workspace_id
                )
            )
        
        # Optionally eager-load relationships if your response schema needs them
        query = query.options(
            selectinload(task_model.Task.assign_to),
            selectinload(task_model.Task.created_by)
        )
        
        tasks = (await db.execute(query)).scalars().all()
        return tasks
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(500, "Database error occurred")

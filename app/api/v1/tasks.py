"""
    this file maintains request of tasks
"""
from typing import List

from fastapi import APIRouter,Depends,HTTPException,status
from app.core.dependencies import require_role,get_current_user
from app.models import team_model, user_model,task_model,organization_model
from app.schemas.task_schema import CreateTask,ResponseTask
from app.core.db import db_dependency
from app.core.logging_config import get_logger
router = APIRouter(
    prefix='/v1/task',
    tags=['Tasks']
)

logger = get_logger(__name__)

# manager/admin can create task
@router.post('/create-task',dependencies=[Depends(require_role(['admin','manager']))],response_model=ResponseTask)
async def add_new_task(task_data:CreateTask,db:db_dependency,
                       current_user: user_model.User = Depends(get_current_user)):
    # verify the team belongs to current user org
    team = (db.query(team_model.Team).filter(team_model.Team.id == task_data.team_id,
                                            team_model.Team.organization_id == current_user.organization_id
                                            ).first())
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Team not found or not in your organization")
    # manager only create task for there team
    if current_user.role == 'manager' and current_user.id != team.leader_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not leader")
    # verify the assign user belongs to same org
    assigned_user = db.query(user_model.User).filter(user_model.User.id == task_data.assign_to,
                                                     user_model.User.organization_id == current_user.organization_id
                                                     ).first()
    if not assigned_user:   # its ensure that assigned_user is None or not
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="assigned user not found.")
    if assigned_user.team_id != task_data.team_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="assigned user is not a team member")
    new_task = task_model.Task(
            title = task_data.title,
            description = task_data.description,
            status = 'pending',
            dead_line = task_data.dead_line,
            team_id=task_data.team_id,
            assign_to = task_data.assign_to,
            created_by = current_user.id
            )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        logger.info(f"task created with title:{task_data.title}.")
        return new_task
    except Exception as e:
        logger.error(f"Database connection error! {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Database error occurred")


# only employee can see their own task
@router.get('/tasks',response_model=List[ResponseTask])
async def get_my_tasks(db:db_dependency,current_user:user_model.User = Depends(get_current_user)):
    try:
        return db.query(task_model.Task).filter(task_model.Task.assign_to == current_user.id).all()
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

# only managers/admin can see there task and progress
@router.get('/progress',dependencies=[Depends(require_role(['manager','admin']))])
async def see_progress(db:db_dependency,current_user:user_model.User = Depends(get_current_user)):
    
    try:
        if current_user.role == 'admin':
            tasks = db.query(task_model.Task).join(team_model.Team,
                                                   team_model.Team.id == task_model.Task.team_id
                                                   ).filter(team_model.Team.organization_id == current_user.organization_id).all()
            return tasks
        else:
            tasks = db.query(task_model.Task).join(team_model.Team,
                                                   team_model.Team.id == task_model.Task.team_id
                                                   ).filter(team_model.Team.leader_id == current_user.id,
                                                    team_model.Team.organization_id == current_user.organization_id
                                                    ).all()
            return tasks
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

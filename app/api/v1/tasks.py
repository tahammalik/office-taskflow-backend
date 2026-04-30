"""
    this file maintains request of tasks
"""
from typing import List

from fastapi import APIRouter,Depends,HTTPException,status
from app.core.dependencies import require_role,get_current_user
from app.models import user_model,task_model
from app.schemas.task_schema import CreateTask,ResponseTask
from app.core.db import db_dependency
from app.core.logging_config import get_logger
router = APIRouter(
    prefix='/v1/task',
    tags=['Tasks']
)

logger = get_logger(__name__)

# manager/admin can create task
@router.post('/create',dependencies=[Depends(require_role(['admin','manager']))],response_model=ResponseTask)
async def add_new_task(task_data:CreateTask,db:db_dependency,
                       current_user: user_model.User = Depends(get_current_user)):

    new_task = task_model.Task(
            title = task_data.title,
            description = task_data.description,
            is_done = task_data.status,
            assigned_to = task_data.assign_to,
            creator_id = current_user.id
        )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        logger.info(f"task created with title:{task_data.title}.")
        return new_task
    except Exception as e:
        logger.error(f"Database connection error! {e}")


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
    if current_user.role == 'admin':
        try:
            return db.query(task_model.Task).all()
        except Exception as e:
            logger.error(f"DB ERROR: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    try:
        return db.query(task_model.Task).filter(task_model.Task.created_by == current_user.id).all()
    except Exception as e:
        logger.error(f"DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

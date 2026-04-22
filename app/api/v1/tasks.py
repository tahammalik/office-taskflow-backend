"""
    this file maintains request of tasks
"""
from typing import List

from fastapi import APIRouter,Depends,HTTPException,status
from app.core.dependencies import require_role,get_current_user
from app.models import user_model,task_model
from app.schemas.task_schema import CreateTask,ResponseTask
from app.core.db import db_dependency
from app.services.task_service import create_task
from logging import getLogger

router = APIRouter(
    prefix='/task/v1',
    tags=['Tasks']
)

logger = getLogger(__name__)

# manager/admin can create task
@router.post('/',dependencies=[Depends(require_role(['admin','manager']))],response_model=ResponseTask)
async def add_new_task(task_data:CreateTask,db:db_dependency,
                       current_user: user_model.User = Depends(get_current_user)):

        new_task = await create_task(task_data=task_data,creator_id=current_user.id,db=db)
        return new_task



# only employee can see their own task
@router.get('/my_tasks',response_model=List[ResponseTask])
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




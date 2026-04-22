from app.core.db import db_dependency
from logging import getLogger
from app.schemas.task_schema import CreateTask
from app.models.task_model import Task


logger = getLogger(__name__)

async def create_task(task_data:CreateTask,creator_id:int,db:db_dependency):
    
    new_task = Task(
        title = task_data.title,
        description = task_data.description,
        is_done = task_data.status,
        assigned_to = task_data.assign_to,
        creator_id = creator_id
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        logger.info(f"task created with title:{task_data.title}.")
        return new_task
    except Exception as e:
        logger.error(f"Database connection error! {e}")



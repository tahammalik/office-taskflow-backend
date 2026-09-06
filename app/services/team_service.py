from logging import getLogger
from fastapi import HTTPException, status
from app.core.db import db_dependency
from app.models.team_model import Team
from app.schemas.team_schema import CreateTeam

logger = getLogger(__name__)


async def create_team(group_data: CreateTeam, db: db_dependency):

    new_group = Team(team_name=group_data.team_name, description=group_data.description)

    try:
        db.add(new_group)
        await db.commit()
        await db.refresh(new_group)
    except Exception as e:
        logger.error("DB ERROR: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )

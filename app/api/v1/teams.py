from fastapi import APIRouter,Depends,HTTPException,status
from app.core.db import db_dependency
from app.schemas.team_schema import CreateTeam
from app.core.dependencies import require_role
from app.models.team_model import Team
from logging import getLogger

router = APIRouter(
    prefix='/groups/v1',
    tags=['Groups']
)

logger = getLogger(__name__)

@router.post('/create_group',dependencies=[Depends(require_role(['manager','admin']))])
async def create_group(group_data:CreateTeam,db:db_dependency):

    new_team = Team(
        team_name = group_data.team_name,
        description = group_data.description
        )
    
    try:
        db.add(new_team)
        db.commit()
        db.refresh(new_team)
        logger.info(f"team created : {new_team.team_name}")
        return new_team
    
    except Exception as e:
        logger.error(f"DB ERROR: %s",e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

@router.delete('/delete/team/{id}')
def delete_team(id:int,db:db_dependency):

    get_team = db.query(Team).filter(Team.id == id).first()

    if get_team:
        try:
            db.delete(get_team)
            db.commit()
            logger.info(f"Organization {id} deleted successfully.")

        except Exception as e:

            logger.error(f"DB ERROR: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail="Database error occurred"
            )

"""
    This is file handle authentication router
"""
from fastapi import APIRouter,HTTPException,status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token_schema import Token
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.db import db_dependency
from app.services.user_service import find_email, authenticate_user
from app.models.user_model import User
from app.core.security import hash_password
from app.core.security import create_access_token
from typing import Annotated
from app.core.exceptions import EmailAlreadyExistsError
from logging import getLogger
from app.core.dependencies import require_role, get_current_user

logger = getLogger(__name__)

router = APIRouter(
    prefix='/auth/v1',
    tags=['Authentication']
    )

@router.post('/user/create',response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def create_user(user_data:UserCreate,db:db_dependency):
    
    email = find_email(user_data.email,db=db)
    if not email:
       raise EmailAlreadyExistsError(message='email already exist')
    new_user = User(
                 username=user_data.username,
                 email = user_data.email,
                 password=hash_password(user_data.password),
                 
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f'user created {new_user.username}')
        return new_user

    except Exception as e:
        
        logger.error(f"DB ERROR: %s",e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


@router.post('/token')
async def token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):

    user = authenticate_user(form_data.username,form_data.password,db=db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Incorrect username or password',
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(data={'sub':str(user.id)})

    return Token(access_token=access_token,token_type='bearer')

@router.get('/me',response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


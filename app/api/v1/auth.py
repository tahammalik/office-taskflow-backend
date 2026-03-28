"""
    This is file handel authentication router 
"""
from fastapi import APIRouter,HTTPException,status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.db import db_dependency
from app.services.auth_service import find_email, authenticate_user
from app.models.user import Users
from app.core.security import hash_password
from app.core.security import create_access_token
from typing import Annotated
from app.core.exceptions import EmailAlreadyExistsError


router = APIRouter(
    prefix='/auth/v1'
    )

@router.post('/create_user',response_model=UserResponse)
async def create_user(user_data:UserCreate,db:db_dependency):
    email = find_email(user_data.email,db=db)
    if email:
       raise EmailAlreadyExistsError()

    new_user = Users(
                 username=user_data.username,
                 email=user_data.email,
                 password=hash_password(user_data.password))
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    except Exception as e:
        db.rollback()
        print(f"DB ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

@router.post('/token')
async def token(from_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):

    user = authenticate_user(from_data.username,from_data.password,db=db)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='wrong user or password')

    access_token = create_access_token(data={'sub':str(user.id),
                                             'username':user.username})

    return Token(access_token=access_token,access_token_type='bearer')


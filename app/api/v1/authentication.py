"""
This is file handle authentication router
"""
import jwt
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status,Response,Request
from fastapi.security import OAuth2PasswordRequestForm
from app.core.db import db_dependency
from app.core.dependencies import get_current_user
from app.core.exceptions import EmailAlreadyExistsError
from app.core.logging_config import get_logger
from app.core.security import (create_access_token,
                               hash_password,
                               create_refresh_token,
                               is_refresh_token_valid_and_revoke,
                               decode_token,
                               revoke_refresh_token)
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.authentication_service import authenticate_user, find_email



# from app.core.dependencies import require_role, get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


# Signup endpoint for creating a new user
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: db_dependency):

    email = await find_email(user_data.email, db=db)
    if email:
        raise EmailAlreadyExistsError(message="email already exist")
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        logger.info(f"user created {new_user.username}")
        return new_user

    except Exception as e:
        await db.rollback()
        logger.error("DB ERROR: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


@router.post("/login")
async def login(response:Response,form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):

    user = await authenticate_user(form_data.username, form_data.password, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": str(user.id)})
    refresh_token = await create_refresh_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="refresh_token",
        secure=True,
        value=refresh_token,
        httponly=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh(request:Request,response:Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing refresh token"
            )
    payload = decode_token(token=refresh_token,expected_type="refresh")
    jti = payload.get("jti")
    username = payload.get("sub")
    if not is_refresh_token_valid_and_revoke(jti=jti):
        raise HTTPException(status_code=401, detail="Refresh token invalid or already used")
    new_access = create_access_token(data={"sub": username})
    new_refresh = create_refresh_token(data={"sub": username})

    response.set_cookie(
         key="refresh_token",
        secure=True,
        value=refresh_token,
        httponly=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60
    )

    return {"access_token": new_access, "token_type": "bearer"}

@router.post("/logout")
async def logout(request:Request,response:Response):
    token = request.cookies.get("refresh_token")
    if token:
        try:
            payload = decode_token(token,expected_type="refresh")
            revoke_refresh_token(payload["jti"])
        except Exception:
            pass
    response.delete_cookie("refresh_token")
    return {"detail":"logout"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get current authenticated user information
    """
    return current_user

"""
This module contains dependencies for the application.
"""

from typing import Annotated, List, Optional

import jwt
from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from app.core.config import SecretConfig
from app.core.db import db_dependency
from app.core.exceptions import UserNotFoundError
from app.models.user_model import User
from app.schemas.token_schema import UserToken
from app.services.authentication_service import find_user

secrets = SecretConfig()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


# dependency to get current user from jwt token
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
    )
    # decode jwt token and extract user information
    try:
        payload = jwt.decode(token, secrets.secret_key, algorithms=[secrets.algorithm])
        id = payload.get("sub")
        if id is None:
            raise credentials_exception

        token_data = UserToken(id=int(id))
    except InvalidTokenError:
        raise credentials_exception

    # find user by id from token data
    user = await find_user(token_data.id, db=db)

    if not user:
        raise UserNotFoundError(message="user not found!")
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user is suspended or deactivated",
        )

    return user


# dependency to check user role
def require_role(allowed_role: List[str]):
    # checks if the user has one of the allowed roles
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]):
        if current_user.role not in allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker

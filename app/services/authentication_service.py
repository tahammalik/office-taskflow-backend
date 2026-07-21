"""
file - auth_service

- Handle basic logic in this project
like find username,find user and many will be used in future
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# from datetime import datetime,timedelta,timezone
from redis import RedisError

from app.core.config import SecretConfig
from app.core.db import db_dependency
from app.core.exceptions import AccountLockedError
from app.core.logging_config import get_logger
from app.core.redis_client import get_redis_client

# from app.schemas.token_schema import Token
from app.core.security import verify_password,hash_password
from app.models.user_model import User

logger = get_logger(__name__)

MAX_FAILED_ATTEMPTS = 4
LOCKOUT_DURATION_MINUTES = 30
REDIS_KEY_PREFIX = "auth:lockout:"


def user_to_response(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "workspace": user.workspace_id,
    }


async def is_email_exist(email: str, db: db_dependency):
    # if user exist return user object else none
    result = await db.scalar(select(User).where(User.email == email))
    return result is not None


# Verify username for not duplicate username exists | return bool value
async def is_username_exist(username: str, db: db_dependency) -> bool:
    # if user exist return true else false
    result = await db.scalar(select(User).where(User.username == username))
    return result is not None


# Verify user and return user object
async def find_user(id, db: db_dependency) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == id))
    return result.scalar_one_or_none()


# string that record failed attempt in redis
def _get_failed_attempt_key(username: str) -> str:
    return f"{REDIS_KEY_PREFIX}attempts:{username}"


# string that record that user is locked
def _get_locked_key(username: str) -> str:
    return f"{REDIS_KEY_PREFIX}locked:{username}"

# record failed attempts in redis
def record_failed_attempt_redis(username: str):

    r = get_redis_client()
    attempt_key = _get_failed_attempt_key(username=username)
    locked_key = _get_locked_key(username=username)
    attempts = r.incr(attempt_key)
  
    if attempts == 1:
        r.expire(attempt_key, LOCKOUT_DURATION_MINUTES * 60)
    if attempts == MAX_FAILED_ATTEMPTS:
        r.setex(locked_key, LOCKOUT_DURATION_MINUTES * 60, "locked")

# redis check that user is lockout or not
def check_account_lockout_redis(username: str):
    r = get_redis_client()
    locked_key = _get_locked_key(username=username)
    # if user locked is true and match in redis return custom error
    if r.exists(locked_key):
        ttl = r.ttl(locked_key)
        raise AccountLockedError(
            message=f"Account locked.Try again after {ttl} seconds"
        )

# reset failed attempts after specific time(default=30min)
def reset_failed_attempts_redis(username: str):

    r = get_redis_client()

    r.delete(_get_failed_attempt_key(username=username))
    r.delete(_get_locked_key(username=username))


# authentication logic to prevent attacks using lockout method
async def authenticate_user(
    username: str, plain_password: str, db: db_dependency
) -> User | None:

    try:
        check_account_lockout_redis(username)
    except RedisError as e:
        print("Redis connection error", e)

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        verify_password(hash_password(SecretConfig().dummy_pass), plain_password=plain_password)
        try:
            record_failed_attempt_redis(username=username)
        except RedisError:
            logger.warning("Failed to record login attempt for %s", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
        )
    # password verification
    if not verify_password(user.password, plain_password):
        try:
            record_failed_attempt_redis(username=username)

        except RedisError:
            logger.warning("Failed to record login attempt for %s", username)

        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

    try:
        reset_failed_attempts_redis(username=username)

    except RedisError:
        print("Failed to reset login attempt for %s", username)

    return user

"""
    file - auth_service

    - Handle basic logic in this project
    like find email,find user and many will be used in future 
"""
from app.core.db import db_dependency
from app.models.user_model import User
from app.schemas.token_schema import Token
from app.core.security import verify_password
from app.core.config import SecretConfig
from typing import Optional
from app.core.exceptions import AccountLockedError
from app.core.redis_client import get_redis_client
from datetime import datetime,timedelta,timezone
from redis import RedisError
from fastapi import HTTPException,status

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
REDIS_KEY_PREFIX = "auth:lockout:"

def user_to_response(user: User) -> dict:
    return {"id": user.id, 
            "username": user.username,
            "role":user.role,
            "organization":user.organization_id
            }

# Verify email for not duplicate email exists | return bool value
def find_email(email:str,db:db_dependency) -> bool:
    return db.query(User).filter(User.email == email).first() is None

# Verify user and return user object
def find_user(id,db:db_dependency) -> Optional[User]:

    return db.query(User).filter(User.id == id).first()
     
# string that record failed attempt in redis
def _get_failed_attempt_key(username: str)-> str:
    return f"{REDIS_KEY_PREFIX}attempts:{username}"
# string that record that user is locked
def _get_locked_key(username:str)-> str:
    return f"{REDIS_KEY_PREFIX}locked:{username}"

# redis check that user is lockout or not
def check_account_lockout_redis(username: str):
    r = get_redis_client()
    locked_key = _get_locked_key(username=username)
    # if user locked is true and match in redis return custom error
    if r.exists(locked_key):
        ttl = r.ttl(locked_key)
        raise AccountLockedError(message=f'Account locked.Try again after {ttl} seconds')
# record failed attempts in redis
def record_failed_attempt_redis(username:str) -> None:

    r = get_redis_client()
    attempt_key = _get_failed_attempt_key(username=username)
    locked_key = _get_locked_key(username=username)
    attempts = r.incr(attempt_key)

    if attempts == 1:
        r.expire(attempt_key,LOCKOUT_DURATION_MINUTES*60)
    if attempts >= MAX_FAILED_ATTEMPTS:
        r.setex(locked_key,LOCKOUT_DURATION_MINUTES*60,'locked')
# reset failed attempts after specific time(default=30min)
def reset_failed_attempts_redis(username:str):

    r = get_redis_client()

    r.delete(_get_failed_attempt_key(username=username))
    r.delete(_get_locked_key(username=username))

# actual authentication happens here
def authenticate_user(username:str,password:str,db:db_dependency) -> HTTPException | None | type[User]:
    
    try:
        check_account_lockout_redis(username)
    except RedisError as e:
        print("Redis connection error",e)

    user = db.query(User).filter(User.username == username).first()

    if not user:
        verify_password(SecretConfig().dummy_hash,password)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        

    if not verify_password(user.password,password):

        try:
            record_failed_attempt_redis(username=username)
        
        except RedisError:
            print("failed record attempt")
        
        return None

            
    try:
        reset_failed_attempts_redis(username=username)

    except RedisError:
        print("Failed to reset login attempt")

    return user
        

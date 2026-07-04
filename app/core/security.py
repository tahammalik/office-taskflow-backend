"""
-------security module-------

This file for handels security related functions like password hashing,
token creation and verification. Here we use argon2 for password hashing and jwt for token
creation and verification. We can also add more security related functions like password reset,
email verification etc in future.
"""

from datetime import datetime, timedelta, timezone
from logging import getLogger
import os
from redis_client import get_redis_client
from fastapi import HTTPException
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import SecretConfig

logger = getLogger(__name__)


secrets = SecretConfig()

# create password hasher using argon2
ph = PasswordHasher(
    time_cost=3, memory_cost=65536, parallelism=4, hash_len=64, salt_len=16
)


# convert plain password to hash
def hash_password(password: str):
    peppered_password = password.encode() + secrets.password_secret_key.encode()

    return ph.hash(peppered_password)


# verify password | hashed_password from db and plain_password from user
def verify_password(hashed_password, plain_password: str):

    # add secret key to password for make it more strong
    peppered_password = plain_password.encode() + secrets.password_secret_key.encode()

    try:
        return ph.verify(hashed_password, peppered_password)
    except VerifyMismatchError:
        return False


# create access token using jwt
async def create_access_token(
    data: dict, expire_timedelta: timedelta = (timedelta(minutes=30))
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_timedelta

    to_encode.update({"exp": expire})
    # create token using updated to_encode object
    encode_jwt = jwt.encode(to_encode, secrets.secret_key, algorithm=secrets.algorithm)

    return encode_jwt


# create refresh token using jwt
async def create_refresh_token(
    data: dict, expire_timedelta: timedelta = (timedelta(days=15))
):
    to_refresh_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_timedelta
    jti = os.urandom(16).hex()
    to_refresh_encode.update({"exp": expire,"type": "refresh","jti":jti})

    refresh_encode_jwt = jwt.encode(
        to_refresh_encode, secrets.secret_key, algorithm=secrets.algorithm
    )
    ttl = int(expire.timestamp() - datetime.now(timezone.utc).timestamp())
    get_redis_client().setex(f"refresh_token:{jti}",ttl,"valid")

    return refresh_encode_jwt
lua_script = """
if redis.call('GET',KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""
atomic_check_and_delete = get_redis_client().register_script(lua_script)

async def decode_token(token:str, expected_type:str):
    try:
        payload = jwt.decode(token,secrets.secret_key, algorithms=[secrets.algorithm])

        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )
        return payload
    except Exception as e:
        logger.error("Exception error!")

async def is_refresh_token_valid_and_revoke(jti: str) -> bool:
    result = atomic_check_and_delete(keys=f"refresh_token:{jti}",args=["valid"])
    return result == 1

async def revoke_refresh_token(jti:str):
    return get_redis_client().delete(f"refresh_token:{jti}")
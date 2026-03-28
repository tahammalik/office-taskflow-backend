"""
    -------security module-------

    This file for handling security related functions like password hashing,
    token creation and verification. Here we use argon2 for password hashing and jwt for token 
    creation and verification. We can also add more security related functions like password reset,
    email verification etc in future.
"""

from datetime import timedelta, datetime, timezone
from argon2 import PasswordHasher
from app.core.config import PASSWORD_SECRET_KEY,SECRET_KEY,ALGORITHM

import jwt


ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=64,
    salt_len=16
)

def hash_password(password: str):
    peppered_password = password.encode() + PASSWORD_SECRET_KEY.encode()

    return ph.hash(peppered_password)

def verify_password(hashed_password:str,plain_password:str):

    peppered_password = plain_password.encode() + PASSWORD_SECRET_KEY.encode()
    
    return ph.verify(hashed_password,peppered_password)



# create access token using jwt
def create_access_token(data:dict,expire_timedelta: timedelta=(timedelta(minutes=15)) ):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_timedelta

    to_encode.update({'exp':expire})
    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)  # create token using updated to_encode object

    return encode_jwt





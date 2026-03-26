"""
    file - auth_service

    - Handle basic logic in this project
    like find email,find user and many will be used in future 
"""
from app.core.db import db_dependency
from app.models.user import Users
from app.schemas.token import Token
from app.core.security import verify_password
from app.core.config import DUMMY_HASH
from typing import Optional

def find_email(email:str,db:db_dependency) -> bool:
    verify_email = db.query(Users).filter(Users.email == email).first()
    if verify_email:
        return True
    else:
        return False
def find_user(id,username,db:db_dependency):
    user = db.query(Users).filter(Users.id == id,
                                  Users.username == username).first()
    if user:
        return user
    else:
        return None

def authenticate_user(username:str,password:str,db:db_dependency):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        verify_password(password,DUMMY_HASH)
        return False
    if not verify_password(user.password,password):
        return False

    return user




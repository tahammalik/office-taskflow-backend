"""
    -------schemas module-------

    Here define pydantic models for user data validation and response formatting.
    1. UserCreate - for validating user creation data (username, email, password)
    2. UserLogin - for validating user login data (username, password)
    3. UserResponse - for formatting user data in responses (id, username, email
    4. GetUser - for formatting user data in responses (id, username)

"""

import re
from uuid import uuid4
from pydantic import BaseModel,Field,field_validator,EmailStr


class UserCreate(BaseModel):

    username: str = Field(...,min_length=3,max_length=50)
    email:EmailStr
    password: str

    @field_validator('username')
    @classmethod
    def username_criteria(cls,v):
    
        if re.search(r'[@#$%&!-]',v):       # check if username has any special characters

            raise ValueError('username must not have special characters')

        return v
    
class UserLogin(BaseModel):
    username:str
    password:str


class UserResponse(BaseModel):
    id: int
    username: str
    email:EmailStr

class GetUser(BaseModel):
    id: int
    username: str
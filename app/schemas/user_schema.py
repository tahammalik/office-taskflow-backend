"""
    -------schemas module-------

    Here define pydantic models for user data validation and response formatting.
    1. UserCreate - for validating user creation data (username, email, password)
    2. UserLogin - for validating user login data (username, password)
    3. UserResponse - for formatting user data in responses (id, username, email
    4. GetUser - for formatting user data in responses (id, username)

"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

    @field_validator('username')
    @classmethod
    def username_criteria(cls, v):
        if re.search(r'[@#$%&!-]', v):
            raise ValueError('username must avoid special characters')
        return v

class UserCreate(UserBase):
    username:str
    email: str
    password: str
    

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    username:str
    email: str
    organization_id: int
    role: str

    

class GetUser(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class UserMinRead(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)
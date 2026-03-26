import re
from uuid import uuid4
from pydantic import BaseModel,Field,field_validator,EmailStr


class UserCreate(BaseModel):

    id:int = Field(default_factory=lambda : uuid4().int % 100_00_00)
    username: str
    email:EmailStr
    password: str

    @field_validator('username')
    @classmethod
    def username_criteria(cls,v):
        if len(v) < 4:
            return "username must be over 8 chars"
        if re.search(r'[@#$%&!-]',v):
            return "username must not have special char"

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
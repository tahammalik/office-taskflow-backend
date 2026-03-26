from pydantic import BaseModel

class UserToken(BaseModel):
    id:int
    username:str

class Token(BaseModel):
    access_token:str
    access_token_type: str
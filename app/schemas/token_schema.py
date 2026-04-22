from pydantic import BaseModel

class UserToken(BaseModel):
    id:int
    

class Token(BaseModel):
    access_token:str
    token_type: str
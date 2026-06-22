from pydantic import BaseModel
from datetime import datetime

class UserToken(BaseModel):
    id:int
    

class Token(BaseModel):
    access_token:str
    token_type: str

class RefreshToken(BaseModel):
        user_id: int
        refresh_token: str
        expire_at: datetime

class TokenResponse(BaseModel):
     refresh_token: str
     token_type: str = "bearer"

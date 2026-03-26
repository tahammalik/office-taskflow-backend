from typing import Annotated
from fastapi import FastAPI
from fastapi.params import Depends
from app.api.v1 import auth
from app.core.db import Base,engine
from app.models.user import Users
from app.core.dependencies import get_current_user
from app.schemas.user import UserResponse
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get('/root')
def message():
    return {"message":"server is running"}

@app.get('/user',response_model=UserResponse)
def get_user(current_user: Annotated[Users,Depends(get_current_user)]):
    return current_user
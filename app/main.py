from typing import Annotated
from fastapi import FastAPI , status
from fastapi.params import Depends
from app.api.v1 import auth
from app.core.db import Base,engine
from app.models.user import Users
from app.core.dependencies import get_current_user
from app.schemas.user import UserResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import UserNotFoundError,EmailAlreadyExistsError
from fastapi.requests import Request
from fastapi.responses import JSONResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(UserNotFoundError)    
async def UserNotFoundError(request: Request,exc:UserNotFoundError):
      return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message":exc.message}
       )   

@app.exception_handler(EmailAlreadyExistsError)
async def EmailAlreadyExistsError(request: Request,exc:EmailAlreadyExistsError):
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message":exc.message}
       )

app.include_router(auth.router)

@app.get('/root')
def message():
    return {"message":"server is running"}

@app.get('/user',response_model=UserResponse)
def get_user(current_user: Annotated[Users,Depends(get_current_user)]):
    return current_user
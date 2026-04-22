from fastapi import FastAPI , status
from app.api.v1 import tasks, user_auth,organization_auth,teams,projects
from app.core.db import Base,engine
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import UserNotFoundError,EmailAlreadyExistsError,AccountLockedError
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
async def user_not_found_error(request: Request,exc:UserNotFoundError):
      return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message":exc.message}
       )   

@app.exception_handler(EmailAlreadyExistsError)
async def email_already_exist_error(request: Request,exc:EmailAlreadyExistsError):
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message":exc.message}
       )

@app.exception_handler(AccountLockedError)
async def account_locked_error(request: Request,exc:AccountLockedError):
     return JSONResponse(
          status_code=status.HTTP_423_LOCKED,
          content={"message":exc.message}
     )

app.include_router(user_auth.router)
app.include_router(tasks.router)
app.include_router(organization_auth.router)
app.include_router(teams.router)
app.include_router(projects.router)

@app.get('/home')
async def home():
      return {"message":"home"}




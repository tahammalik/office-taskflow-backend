<<<<<<< Updated upstream
from fastapi import FastAPI , status
from app.api.v1 import tasks, authentication,enterprise_auth,teams,projects
from app.core.db import Base,engine
=======
from fastapi import FastAPI, status
>>>>>>> Stashed changes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

<<<<<<< Updated upstream
#Base.metadata.create_all(bind=engine)
#Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(app: FastAPI):
      async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
=======
from app.api.v1 import authentication, enterprise_auth, projects, tasks, teams
from app.core.db import Base, engine
from app.core.exceptions import (
    AccountLockedError,
    EmailAlreadyExistsError,
    UserNotFoundError,
)
>>>>>>> Stashed changes

      yield 

app = FastAPI(title="Office TaskFlow - Enterprise Edition",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


<<<<<<< Updated upstream
@app.exception_handler(UserNotFoundError)    
async def user_not_found_error(request: Request,exc:UserNotFoundError):
      return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message":exc.message}
       )   
=======
@app.exception_handler(UserNotFoundError)
async def user_not_found_error(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"message": exc.message}
    )

>>>>>>> Stashed changes

@app.exception_handler(EmailAlreadyExistsError)
async def email_already_exist_error(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"message": exc.message}
    )


@app.exception_handler(AccountLockedError)
async def account_locked_error(request: Request, exc: AccountLockedError):
    return JSONResponse(
        status_code=status.HTTP_423_LOCKED, content={"message": exc.message}
    )

<<<<<<< Updated upstream
app.include_router(authentication.router)
=======

app.include_router(authentication.router)
app.include_router(tasks.router)
>>>>>>> Stashed changes
app.include_router(enterprise_auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(teams.router)


@app.get("/")
async def home():
    return {"message": "server is running - Enterprise Edition"}

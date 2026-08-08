from fastapi import FastAPI , status
from app.api.v1 import tasks, authentication, workspace,teams,projects
from app.core.db import Base,engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.exceptions import *
from app.core.logging_config import setup_logging
from sqlalchemy import text
from app.core.logging_config import get_logger
from fastapi.responses import JSONResponse


logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
        setup_logging()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield 
        await engine.dispose()

app = FastAPI(title="taskio",lifespan=lifespan)

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
async def email_already_exist_error(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"message": exc.message}
    )


@app.exception_handler(AccountLockedError)
async def account_locked_error(request: Request, exc: AccountLockedError):
    return JSONResponse(
        status_code=status.HTTP_423_LOCKED, content={"message": exc.message}
    )

app.include_router(authentication.router)
app.include_router(workspace.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(teams.router)


@app.get("/health")
async def health_check():
    try:
        with engine.connect() as connection:
           connection.execute(text("SELECT 1"))

        return {
             "status":"healthy",
             "database":"connected"
        }
    except Exception as e:
        logger.error("SERVICE UNAVILABLE: %s",e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content= {"status":"unhealthy","error":str(e)}
        )



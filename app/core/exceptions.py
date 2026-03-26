from fastapi import FastAPI,status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from uvicorn import run

app = FastAPI()

class UserNotFoundError(Exception):
    def __init__(self,message):
        self.message = message


@app.exception_handler(UserNotFoundError)
def find_user(request: Request,exc:UserNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message":exc.message}
    )   
users = ["john","doe","alice"]
@app.get('/user/{user_name}')
def get_user(user_name:str):
    if user_name not in users:
        raise UserNotFoundError(message=f"user with name {user_name} not found")
    return {"user":user_name}

if __name__ == "__main__":
    run(app,host='localhost',port=8000)
import sqlite3
import requests
from fastapi import FastAPI, Depends
from starlette.config import Config
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, status
from jose import JWTError, jwt

SERVICE = 'tasks'
DB_NAME = f"{SERVICE}.db"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

app = FastAPI()

con = sqlite3.connect(DB_NAME)

class User(BaseModel):
    username: str


class TokenData(BaseModel):
    username: str | None = None

class Task(BaseModel):
    description: str
    assignee: str
    initial_cost: int
    done_cost: int

def get_user(username: str):
    cur = con.cursor()
    res = cur.execute(f"SELECT username FROM users WHERE username='{username}'")
    result = res.fetchone()
    if result:
        return User(username=result[0])
    

def create_user(user: User):
    cur = con.cursor()
    cur.execute(f"insert into users values ('{user.__hash__username}')")
    con.commit()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    print(token_data)
    user = get_user(username=token_data.username)
    if user is None:
        user = User(username=token_data.username)
        create_user(user)
    return user


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    response = requests.post('http://sso:8000/token', data=dict(username=form_data.username,
                                              password=form_data.password))
    return response.json()


@app.get("/tasks")
async def tasks(
    current_user: Annotated[User, Depends(get_current_user)]
):
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM tasks WHERE assignee='{current_user.username}'")
    result = res.fetchall()
    return [Task(description=r[0], assignee=r[1], initial_cost=r[2], done_cost=r[3]) for r in result]
    
    


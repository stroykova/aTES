import sqlite3
from typing import Annotated
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

SERVICE = 'sso'
DB_NAME = f"{SERVICE}.db"

app = FastAPI()
con = sqlite3.connect(DB_NAME)


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


def get_user(username: str):
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM users")
    print(res.fetchall())

    cur = con.cursor()
    res = cur.execute(f"SELECT username, hashed_password FROM users WHERE username='{username}'")
    result = res.fetchone()
    print(result)
    if result:
        return UserInDB(username=result[0], hashed_password=result[1])
    

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user



@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    print(form_data.username)
    user = get_user(form_data.username)
    print(user)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
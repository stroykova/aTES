import sqlite3
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

SERVICE = 'sso'
DB_NAME = f"{SERVICE}.db"

app = FastAPI()
con = sqlite3.connect(DB_NAME)


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    email: str


class UserInDB(User):
    hashed_password: str


def get_user(email: str):
    cur = con.cursor()
    res = cur.execute(f"SELECT email, hashed_password FROM users WHERE email='{email}'")
    result = res.fetchone()
    if result:
        return UserInDB(email=result[0], hashed_password=result[1])
    

@app.get("/")
async def root():
    return {"message": "Hello World"}

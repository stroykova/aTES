import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
SERVICE = 'accounting'
DB_NAME = f"{SERVICE}.db"

app = FastAPI()
con = sqlite3.connect(DB_NAME)


@app.get("/")
async def root():
    return {"message": "Hello World"}


class User(BaseModel):
    username: str
    balance: int

@app.get("/users")
async def users():
    cur = con.cursor()
    statement = f"SELECT * FROM users"
    res = cur.execute(statement)
    result = res.fetchall()
    print(result)
    return [User(
        username=r[0], 
        balance=r[1], 
        ) for r in result]
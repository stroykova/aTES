import sqlite3
from fastapi import FastAPI

SERVICE = 'template'
DB_NAME = f"{SERVICE}.db"

app = FastAPI()
con = sqlite3.connect(DB_NAME)


@app.get("/")
async def root():
    return {"message": "Hello World"}

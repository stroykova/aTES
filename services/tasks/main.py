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
import random
from kafka import KafkaProducer
import json
import uuid
from datetime import datetime
from schemas.schemas.tasks.TaskCreated.v1 import TaskCreatedV1, TaskV1
from schemas.schemas.tasks.TasksShuffled.v1 import TasksShuffledV1
from schemas.schemas.tasks.TaskDone.v1 import TaskDoneV1, TaskV1 as TaskDoneDataV1

SERVICE = 'tasks'
DB_NAME = f"{SERVICE}.db"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
producer = KafkaProducer(bootstrap_servers=['kafka:29092', 'kafka2:29093'], api_version=(0, 10, 1))
app = FastAPI()

con = sqlite3.connect(DB_NAME)

class User(BaseModel):
    username: str
    role: str


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None


class TaskBase(BaseModel):
    description: str

class DoneTask(BaseModel):
    id: int

class Task(TaskBase):
    id: int
    assignee: str
    initial_cost: int
    done_cost: int
    status: str | None = None


def event(topic, data: BaseModel):
    print('send event:', topic, data)
    producer.send(topic, data.model_dump_json().encode('utf-8'))
    producer.flush()


def get_user(username: str):
    cur = con.cursor()
    res = cur.execute(f"SELECT username, role FROM users WHERE username='{username}'")
    result = res.fetchone()
    if result:
        return User(username=result[0], role=result[1])
    

def create_user(user: User):
    cur = con.cursor()
    cur.execute(f"insert into users values ('{user.username}', '{user.role}')")
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
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    print(token_data)
    user = get_user(username=token_data.username)
    if user is None:
        user = User(username=token_data.username, role=token_data.role)
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
    if current_user.role == 'parrot':
        statement = f"SELECT * FROM tasks WHERE assignee='{current_user.username}'"
    else:
        statement = f"SELECT * FROM tasks"
    res = cur.execute(statement)
    result = res.fetchall()
    return [Task(id=r[0], description=r[1], assignee=r[2], initial_cost=r[3], done_cost=r[4], status=r[5]) for r in result]
    
    

@app.post("/tasks")
async def create_task(
    current_user: Annotated[User, Depends(get_current_user)],
    task: TaskBase, 
):
    cur = con.cursor()
    random_statement = 'SELECT username FROM users where role = "parrot" ORDER BY RANDOM() LIMIT 1;'
    res = cur.execute(random_statement).fetchone()[0]
    initial_cost = random.randint(-20, -10)
    done_cost = random.randint(20, 40)
    statement = f"insert into tasks ('description', 'assignee', 'initial_cost', 'done_cost') values ('{task.description}', '{res}', '{initial_cost}', '{done_cost}')"
    cur.execute(statement)
    con.commit()

    event(
        'tasks_stream', 
        TaskCreatedV1(
            event_id=uuid.uuid4(),
            event_version=1,
            event_domain='tasks',
            event_name='TaskCreated',
            event_time=datetime.now().isoformat(),
            producer='tasks',
            data=TaskV1(
                **task.model_dump()
            ),
        ),
    )
    return 'ok'


@app.post("/tasks/shuffle")
async def shuffle(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role not in ('manager', 'admin'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="role",
            headers={"WWW-Authenticate": "Bearer"},
        )
    cur = con.cursor()
    statement = 'SELECT username FROM users where role = "parrot";'
    names = [n[0] for n in cur.execute(statement).fetchall()]
    print(names)
    statement = 'SELECT id FROM tasks'
    ids = [n[0] for n in cur.execute(statement).fetchall()]
    print(ids)
    cases = ' '.join(
        f"when {_id} then '{random.choice(names)}'" for _id in ids
    )
    statement = (
        f"update tasks set assignee = case id {cases} end where id in ({','.join(str(_id) for _id in ids)})"
    )
    print(statement)
    cur.execute(statement)
    con.commit()
    event(
        'tasks_stream', 
        TasksShuffledV1(
            event_id=uuid.uuid4(),
            event_version=1,
            event_domain='tasks',
            event_name='TasksShuffled',
            event_time=datetime.now().isoformat(),
            producer='tasks',
            data={},
        ),
    )
    return 'ok'


@app.post("/tasks/done")
async def done(
    current_user: Annotated[User, Depends(get_current_user)],
    task: DoneTask
):
    if current_user.role != 'parrot':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="role",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    cur = con.cursor()
    statement = (
        f"update tasks set status = 'done' where id = {task.id}"
    )
    print(statement)
    cur.execute(statement)
    con.commit()
    event(
        'tasks_stream', 
        TaskDoneV1(
            event_id=uuid.uuid4(),
            event_version=1,
            event_domain='tasks',
            event_name='TaskDone',
            event_time=datetime.now().isoformat(),
            producer='tasks',
            data=TaskDoneDataV1(**task.model_dump()),
        ),
    )
    return 'ok'
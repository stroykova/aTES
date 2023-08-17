import sqlite3
import uuid
from datetime import datetime
from typing import Annotated
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json
from schemas.schemas.auth.AccountCreated.v1 import AccountCreatedV1, UserV1

producer = KafkaProducer(bootstrap_servers=['kafka:29092', 'kafka2:29093'], api_version=(0, 10, 1))

SERVICE = 'sso'
DB_NAME = f"{SERVICE}.db"

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
con = sqlite3.connect(DB_NAME)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def event(topic, data: BaseModel):
    print('send event:', topic, data)
    producer.send(topic, data.model_dump_json().encode('utf-8'))
    producer.flush()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

class User(BaseModel):
    username: str
    role: str


class UserInDB(User):
    hashed_password: str


class UserRegister(User):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None


def get_user(username: str):
    cur = con.cursor()
    res = cur.execute(f"SELECT username, hashed_password, role FROM users WHERE username='{username}'")
    result = res.fetchone()
    if result:
        return UserInDB(username=result[0], hashed_password=result[1], role=result[2])
    

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


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
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user



@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@app.post("/register")
async def register(u: UserRegister):
    statement = f"insert into users values ('{u.username}', '{u.password}', '{u.role}')"
    cur = con.cursor()
    cur.execute(statement)
    con.commit()
    event(
        'accounts_stream', 
        AccountCreatedV1(
            event_id=uuid.uuid4(),
            event_version=1,
            event_domain='auth',
            event_name='AccountCreated',
            event_time=datetime.now().isoformat(),
            producer='sso',
            data=UserV1(
                username=u.username, 
                role=u.role
            ),
        ),
    )
    return 'ok'
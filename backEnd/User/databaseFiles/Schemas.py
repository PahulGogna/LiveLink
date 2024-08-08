from pydantic import BaseModel,EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id : Optional[int] = None


class User(BaseModel):
    name: str
    email: EmailStr


class login(BaseModel):
    email: EmailStr
    password: str


class create_user(User):
    password: str


class update_post(BaseModel):
    running: bool


class post(BaseModel):
    url:str
    by: int = None
    status_code: int = None
    working: bool = True
    running: bool = False
    exception: bool = False
    error: str = None

class UserInDB(User):
    password: str
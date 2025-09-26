# models.py
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordUpdate(BaseModel):
    new_password: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_shared: bool = False


class Task(TaskCreate):
    id: int
    done: bool
    owner_id: int
    is_shared: bool
    created_at: str


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

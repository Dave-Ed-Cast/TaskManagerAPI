from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: str | None = None

class Task(TaskCreate):
    id: int
    done: bool
    owner_id: int

class PasswordUpdate(BaseModel):
    new_password: str
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..database import crud, models
from ..database.dependencies import get_current_user, admin_required

router = APIRouter()


@router.post("/")
def create_task(task: models.TaskCreate, user=Depends(get_current_user)):
    user_id, _, _ = user
    crud.create_task(task.title, task.description, user_id)
    return {"msg": "Task created successfully"}

@router.get("/")
def list_tasks(user=Depends(get_current_user)):
    user_id, _, _ = user
    tasks = crud.get_tasks(user_id)
    return [{"id": t[0], "title": t[1], "description": t[2], "done": t[3], "owner_id": t[4]} for t in tasks]

# Example for admin-only route
@router.get("/all")
def list_all_tasks(admin=Depends(admin_required)):
    tasks = crud.get_all_tasks()
    return [{"id": t[0], "title": t[1], "description": t[2], "done": t[3], "owner_id": t[4]} for t in tasks]

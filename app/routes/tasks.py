from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..database import crud, models
from ..database.dependencies import get_current_user, admin_required

router = APIRouter()


# ===== POST methods =====
@router.post("/", response_model=dict)
def create_task(task: models.TaskCreate, user=Depends(get_current_user)):
    user_id, _, _ = user
    crud.create_task(task.title, task.description, user_id)
    return {"msg": "Task created successfully"}


# ===== GET methods =====
#fetch tasks for user, either admin or not
@router.get("/", response_model=list[dict])
def list_tasks_for_user(current_user: dict = Depends(get_current_user)):
    rows = crud.get_tasks_for_user(current_user)
    return [
        {"id": t[0], "title": t[1], "description": t[2], "done": bool(t[3]), "owner_id": t[4]}
        for t in rows
    ]
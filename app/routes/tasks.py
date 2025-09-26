from fastapi import APIRouter, Depends
from ..database import crud, models
from ..database.dependencies import get_current_user

router = APIRouter()


# ===== POST methods =====
@router.post("/", response_model=dict)
def create_task(task: models.TaskCreate, user=Depends(get_current_user)):
    user_id = user["id"]
    is_admin_user = user["is_admin"]

    
    # Only admins can create shared tasks
    is_shared_task = task.is_shared and is_admin_user

    task_id = crud.create_task(task.title, task.description, user_id, is_shared_task)
    return {"message": "Task created successfully", "task_id": task_id}


# ===== GET methods =====
#fetch tasks for user, either admin or not
@router.get("/", response_model=list[dict])
def list_tasks_for_user(current_user: dict = Depends(get_current_user)):
    return crud.get_tasks_for_user(current_user)

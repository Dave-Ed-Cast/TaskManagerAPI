from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .. import crud, models, auth

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> tuple:

    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")

        if username is None: raise HTTPException(status_code=401, detail="Invalid token")    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = crud.get_user(username)

    if user is None: raise HTTPException(status_code=404, detail="User not found")
    return user

def admin_required(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@router.post("/")
def create_task(task: models.TaskCreate, user=Depends(get_current_user)):

    user_id, _, _ = user
    crud.create_task(task.title, task.description, user_id)
    return {"msg": "Task created successfully"}

@router.get("/")
def list_tasks(user=Depends(get_current_user)):

    user_id, _, _ = user
    tasks = crud.get_tasks(user_id)
    return [
        {"id": t[0], "title": t[1], "description": t[2], "done": t[3], "owner_id": t[4]}
        for t in tasks
    ]


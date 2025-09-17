from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, timezone
from ..database import auth, crud, models
from ..database.crud import delete_user
from .tasks import get_current_user
from ..constants import (
    USERNAME_TAKEN_EX, INVALID_CREDENTIALS_EX, 
    TOKEN_EXPIRATION, USER_NOT_FOUND_EX
)

router = APIRouter()


@router.post("/register")
def register(user: models.UserCreate):
    existing = crud.get_user(user.username)

    # The truthy statements symbolizes that the get_user actually returns something
    # And is not None, False, 0, "", [], {}, etc.
    if existing: raise HTTPException(USERNAME_TAKEN_EX)

    user_data = crud.create_user(user.username, user.password, user.is_admin)
    return user_data


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user(form_data.username)

    if not db_user: raise HTTPException(INVALID_CREDENTIALS_EX)

    _, username, hashed_password, is_admin = db_user
    
    psw_match = auth.verify_password(form_data.password, hashed_password)
    if not psw_match: raise HTTPException(INVALID_CREDENTIALS_EX)

    access_token_expires = timedelta(minutes=TOKEN_EXPIRATION)
    token = auth.create_access_token(
        data={"sub": username, "is_admin": bool(is_admin)},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer", "is_admin": bool(is_admin)}


@router.get("/all")
def list_users():
    from app.database.database import get_db

    with get_db() as connection:
        cursor = connection.cursor()
        read_query = "SELECT id, username, is_admin FROM users"
        cursor.execute(read_query)
        users = cursor.fetchall()
        
    return [{"id": user[0], "username": user[1], "is_admin": user[2]} for user in users]


@router.delete("/{username}")
def remove_user(username: str, current_user=Depends(auth.admin_required)):
    success = delete_user(username)
    if not success: raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User '{username}' deleted"}


@router.put("/{username}/role")
def change_role(username: str, is_admin: bool, current_user=Depends(auth.admin_required)):
    from ..database.crud import update_user_role

    success = update_user_role(username, is_admin)
    if not success: raise HTTPException(USER_NOT_FOUND_EX)

    return {"message": f"Role updated for {username}"}


@router.post("/")
def create_task(task: models.TaskCreate, user=Depends(get_current_user)):
    user_id, _, _ = user
    crud.create_task(task.title, task.description, user_id)

    return {"msg": "Task created successfully"}


@router.get("/")
def list_tasks(user=Depends(get_current_user)):
    user_id, _, _ = user
    tasks = crud.get_tasks(user_id)

    return [{"id": t[0], "title": t[1], "description": t[2],"done": t[3], "owner_id": t[4]} for t in tasks]

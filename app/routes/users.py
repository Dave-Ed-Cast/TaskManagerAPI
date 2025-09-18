from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from ..database import auth, crud, models, database
from ..database.dependencies import get_current_user, admin_required
from ..constants import (INVALID_CREDENTIALS_EX, TOKEN_EXPIRATION, USER_NOT_FOUND_EX)

router = APIRouter()


# ===== POST methods =====
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user(form_data.username)

    if not db_user:
        raise HTTPException(INVALID_CREDENTIALS_EX)

    _, username, hashed_password, is_admin = db_user

    psw_match = auth.verify_password(form_data.password, hashed_password)
    if not psw_match:
        raise HTTPException(INVALID_CREDENTIALS_EX)

    access_token_expires = timedelta(minutes=TOKEN_EXPIRATION)
    token = auth.create_access_token(
        data={"sub": username, "is_admin": bool(is_admin)},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer", "is_admin": bool(is_admin)}


@router.post("/create", include_in_schema=False)
def create_task(task: models.TaskCreate, user=Depends(get_current_user)):
    user_id, _, _ = user
    crud.create_task(task.title, task.description, user_id)

    return {"msg": "Task created successfully"}


# ===== GET methods =====
@router.get("users/all", include_in_schema=False)
def list_users(admin=Depends(admin_required)):
    # logging purposes
    admin_username = admin.get("sub", "unknown")
    print(f"[ADMIN ACTION] Admin '{admin_username}' listed all users at {datetime.now()}")

    with database.get_db() as connection:
        cursor = connection.cursor()
        read_query = "SELECT id, username, is_admin FROM users"
        cursor.execute(read_query)
        users = cursor.fetchall()

    return [{"id": user[0], "username": user[1], "is_admin": user[2]} for user in users]


@router.get("/all", include_in_schema=False)
def list_all_tasks(admin=Depends(admin_required)):

    # logging purposes
    admin_username = admin.get("sub", "unknown")
    print(f"[ADMIN ACTION] Admin '{admin_username}' listed all tasks at {datetime.now()}")
    tasks = crud.get_all_tasks()
    return [{"id": t[0], "title": t[1], "description": t[2], "done": t[3], "owner_id": t[4]} for t in tasks]


@router.get("/")
def list_tasks(user=Depends(get_current_user)):
    user_id, _, _ = user
    tasks = crud.get_tasks(user_id)

    return [{"id": t[0], "title": t[1], "description": t[2], "done": t[3], "owner_id": t[4]} for t in tasks]


# ===== DELETE methods =====
@router.delete("/{username}")
def remove_user(username: str, admin=Depends(admin_required)):
    # logging purposes
    admin_username = admin.get("sub", "unknown")
    print(f"[ADMIN ACTION] Admin '{admin_username}' is deleting user '{username}' at {datetime.now()}")

    # Perform the deletion
    success = crud.delete_user(username)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)

    return {"message": f"User '{username}' deleted successfully"}


# ===== PUT methods =====
@router.put("/{username}/role")
def change_role(username: str, is_admin: bool, admin=Depends(admin_required)):
    # logging purposes
    admin_username = admin.get("sub", "unknown")
    print(f"[ADMIN ACTION] Admin '{admin_username}' is deleting user '{username}' at {datetime.now()}")

    success = crud.update_user_role(username, is_admin)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)

    return {"message": f"Role updated for {username}"}


@router.put("/{username}/password")
def admin_reset_password(username: str, data: models.PasswordUpdate, admin=Depends(admin_required)):
    # logging purposes
    admin_username = admin.get("sub", "unknown")
    print(f"Admin '{admin_username}' is resetting password for user '{username}' at {datetime.now()}")

    success = crud.update_user_password(username, data.new_password)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)
    return {"msg": f"Password for '{username}' has been updated successfully"}

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from ..database import auth, crud, models, database
from ..database.dependencies import get_current_user, admin_required
from ..constants import (
    USERNAME_TAKEN_EX, INVALID_CREDENTIALS_EX, 
    TOKEN_EXPIRATION_MINS, USER_NOT_FOUND_EX, DELETING_SELF_EX
)

router = APIRouter()


# ===== POST methods =====
@router.post("/register")
def register(user: models.UserCreate):
    existing = crud.get_user(user.username)

    # The truthy statements symbolizes that the get_user actually returns something
    # And is not None, False, 0, "", [], {}, etc.
    if existing:
        raise HTTPException(USERNAME_TAKEN_EX)

    user_data = crud.create_user(user.username, user.password, user.is_admin)
    return user_data


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user(form_data.username)

    if not db_user:
        raise HTTPException(INVALID_CREDENTIALS_EX)

    _, username, hashed_password, is_admin = db_user

    psw_match = auth.verify_password(form_data.password, hashed_password)
    if not psw_match:
        raise HTTPException(INVALID_CREDENTIALS_EX)

    access_token_expires = timedelta(minutes=TOKEN_EXPIRATION_MINS)
    token = auth.create_access_token(
        data={"sub": username, "is_admin": bool(is_admin)},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer", "is_admin": bool(is_admin)}


@router.post("/")
def create_task(task: models.TaskCreate, user=Depends(get_current_user)):
    user_id, _, _ = user
    crud.create_task(task.title, task.description, user_id)

    return {"msg": "Task created successfully"}


# ===== GET methods =====
@router.get("/all")
# by defining this input parameter, we don't allow users nor admins to manipulate URLs
def list_users(_=Depends(admin_required)):

    with database.get_db() as connection:
        cursor = connection.cursor()
        read_query = "SELECT id, username, is_admin FROM users"
        cursor.execute(read_query)
        users = cursor.fetchall()

    return [{"id": user[0], "username": user[1], "is_admin": user[2]} for user in users]


@router.get("/")
def list_tasks(user=Depends(get_current_user)):
    user_id, _, _ = user
    tasks = crud.get_tasks(user_id)

    return [{"id": t[0], "title": t[1], "description": t[2], "done": t[3], "owner_id": t[4]} for t in tasks]


# ===== PUT methods =====
@router.put("/{username}/role")
def change_role(username: str, is_admin: bool, admin=Depends(admin_required)):
    # logging purposes
    admin_username = admin.get("sub", "unknown")
    print(f"[ADMIN ACTION] Admin '{admin_username}' is changing role for user '{username}' at {datetime.now()}")

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

# ===== DELETE methods =====


@router.delete("/{username}")
def remove_user(username: str, admin=Depends(admin_required)):
    # logging purposes
    admin_username = admin.get("sub", "unknown")
    if username == admin_username:
        raise HTTPException(DELETING_SELF_EX)
    
    print(f"[ADMIN ACTION] Admin '{admin_username}' is deleting user '{username}' at {datetime.now()}")

    success = crud.delete_user(username)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)

    return {"message": f"User '{username}' deleted"}

import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from ..database import auth, crud, models, database
from ..database.dependencies import get_current_user, admin_required
from ..constants import (
    USERNAME_TAKEN_EX, INVALID_CREDENTIALS_EX,
    TOKEN_EXPIRATION_MINS, USER_NOT_FOUND_EX, DELETING_SELF_EX
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ===== POST methods =====
@router.post("/register")
def register(user: models.UserCreate):
    existing = crud.get_user(user.username)

    # The truthy statements symbolizes that the get_user actually returns something
    # And is not None, False, 0, "", [], {}, etc.
    if existing:
        raise HTTPException(USERNAME_TAKEN_EX)

    return crud.create_user(user.username, user.password, user.is_admin)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user(form_data.username)

    if not db_user:
        raise HTTPException(INVALID_CREDENTIALS_EX)
    if not db_user:
        raise HTTPException(INVALID_CREDENTIALS_EX)

    psw_match = auth.verify_password(form_data.password, db_user["hashed_password"])
    if not psw_match:
        raise HTTPException(INVALID_CREDENTIALS_EX)

    access_token_expires = timedelta(minutes=TOKEN_EXPIRATION_MINS)
    token = auth.create_access_token(
        data={"sub": db_user["username"], "user_id": db_user["id"], "is_admin": db_user["is_admin"]},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer", "is_admin": db_user["is_admin"]}


# ===== GET methods =====
# with the input parameter, nobody can manipulate this URL
@router.get("/all")
def list_users(_=Depends(admin_required)):

    with database.get_db() as connection:
        cursor = connection.cursor()
        read_query = "SELECT id, username, is_admin FROM users"
        cursor.execute(read_query)
        users = cursor.fetchall()


    return [{"id": user[0], "username": user[1], "is_admin": user[2]} for user in users]


# ===== PUT methods =====
@router.put("/{username}/password")
def admin_reset_password(username: str, data: models.PasswordUpdate, admin=Depends(admin_required)):
    admin_username = admin["username"]
    logger.info(f"Admin {admin_username} is resetting password for user '{username}'")

    success = crud.update_user_password(username, data.new_password)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)
    return {"message": f"Password for '{username}' has been updated successfully"}


@router.put("/{username}/role")
def change_user_role(username: str, is_admin: bool, current_admin=Depends(admin_required)):
    if current_admin["username"] == username:
        raise HTTPException(DELETING_SELF_EX)

    if not crud.update_user_role(username, is_admin):
        raise HTTPException(USER_NOT_FOUND_EX)
    
    new_role = "Admin" if is_admin else "User"
    return {"message": f"User '{username}' role updated to {new_role}"}


# ===== DELETE methods =====
@router.delete("/{username}")
def remove_user(username: str, admin=Depends(admin_required)):
    admin_username = admin["username"]
    if username == admin_username:
        raise HTTPException(DELETING_SELF_EX)
    

    logger.warning(f"Admin {admin_username} is deleting user '{username}'")
    success = crud.delete_user(username)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)

    return {"message": f"User '{username}' deleted"}
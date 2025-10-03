import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
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
async def register(user: models.UserCreate):
    existing = await crud.get_user(user.username)
    if existing:
        raise HTTPException(USERNAME_TAKEN_EX)

    return await crud.create_user(user.username, user.password, user.is_admin)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await crud.get_user(form_data.username)
    if not db_user or not auth.verify_password(form_data.password, db_user["hashed_password"]):
        raise HTTPException(INVALID_CREDENTIALS_EX)

    access_token_expires = timedelta(minutes=TOKEN_EXPIRATION_MINS)
    token = auth.create_access_token(
        data={"sub": db_user["username"], "user_id": db_user["id"], "is_admin": db_user["is_admin"]},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer", "is_admin": db_user["is_admin"]}


# ===== GET methods =====
@router.get("/all")
async def list_users(_=Depends(admin_required)):
    async with database.get_db() as connection:
        cursor = await connection.execute("SELECT id, username, is_admin FROM users")
        users = await cursor.fetchall()

    return [{"id": user[0], "username": user[1], "is_admin": user[2]} for user in users]


# ===== PUT methods =====
@router.put("/{username}/password")
async def admin_reset_password(username: str, data: models.PasswordUpdate, admin=Depends(admin_required)):
    logger.info(f"Admin {admin['username']} is resetting password for user '{username}'")
    success = await crud.update_user_password(username, data.new_password)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)
    return {"message": f"Password for '{username}' has been updated successfully"}


@router.put("/{username}/role")
async def change_user_role(username: str, is_admin: bool, current_admin=Depends(admin_required)):
    if current_admin["username"] == username:
        raise HTTPException(DELETING_SELF_EX)

    if not await crud.update_user_role(username, is_admin):
        raise HTTPException(USER_NOT_FOUND_EX)

    new_role = "Admin" if is_admin else "User"
    return {"message": f"User '{username}' role updated to {new_role}"}


# ===== DELETE methods =====
@router.delete("/{username}")
async def remove_user(username: str, admin=Depends(admin_required)):
    if username == admin["username"]:
        raise HTTPException(DELETING_SELF_EX)

    logger.warning(f"Admin {admin['username']} is deleting user '{username}'")
    success = await crud.delete_user(username)
    if not success:
        raise HTTPException(USER_NOT_FOUND_EX)

    return {"message": f"User '{username}' deleted"}

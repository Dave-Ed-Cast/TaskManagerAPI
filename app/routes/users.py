from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from datetime import timedelta

from .. import crud, auth, models
from ..crud import delete_user

router = APIRouter()

@router.post("/register")
def register(user: models.UserCreate):
    existing = crud.get_user(user.username)
    if existing: raise HTTPException(status_code=400, detail="Username already taken")
    user_data = crud.create_user(user.username, user.password, user.is_admin)
    return user_data

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user(form_data.username)
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user_id, username, hashed_password, is_admin = db_user
    if not auth.verify_password(form_data.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth.create_access_token(
        data={"sub": username, "is_admin": bool(is_admin)},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer", "is_admin": bool(is_admin)}


@router.get("/all")
def list_users():
    from app.database import get_db

    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, is_admin FROM users")
        users = cursor.fetchall()

    return [{"id": u[0], "username": u[1], "is_admin": u[2]} for u in users]

@router.delete("/{username}")
def remove_user(username: str, current_user=Depends(auth.admin_required)):
    success = delete_user(username)
    if not success: raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User '{username}' deleted"}

from fastapi import APIRouter, HTTPException, Depends

@router.put("/{username}/role")
def change_role(username: str, is_admin: bool, current_user=Depends(auth.admin_required)):
    from ..crud import update_user_role
    
    success = update_user_role(username, is_admin)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"Role updated for {username}"}

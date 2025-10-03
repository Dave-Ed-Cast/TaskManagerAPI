from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .crud import get_user
from ..constants import (
    USER_NOT_FOUND_EX, INVALID_TOKEN_EX, 
    ADMIN_REQUIRED_EX, SECRET_KEY, ALGORITHM
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(INVALID_TOKEN_EX)
    except JWTError:
        raise HTTPException(INVALID_TOKEN_EX)

    user = await get_user(username)
    if user is None:
        raise HTTPException(USER_NOT_FOUND_EX)
    return user


async def admin_required(current_user: dict = Depends(get_current_user)) -> dict:
    if not current_user.get("is_admin", False):
        raise HTTPException(ADMIN_REQUIRED_EX)
    return current_user

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..database import crud, auth
from ..constants import USER_NOT_FOUND_EX, INVALID_TOKEN_EX, ADMIN_REQUIRED_EX

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> tuple:

    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")

        if username is None: raise HTTPException(INVALID_TOKEN_EX)    
    except JWTError:
        raise HTTPException(INVALID_TOKEN_EX)

    user = crud.get_user(username)

    if user is None: raise HTTPException(USER_NOT_FOUND_EX)
    return user

def admin_required(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        if not payload.get("is_admin"): raise HTTPException(ADMIN_REQUIRED_EX)

        return payload
    except JWTError:
        raise HTTPException(INVALID_TOKEN_EX)
    


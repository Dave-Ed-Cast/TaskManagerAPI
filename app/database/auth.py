from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..constants import (
    SECRET_KEY, ALGORITHM, TOKEN_EXPIRATION,
    INVALID_TOKEN_EX, ADMIN_REQUIRED_EX
)


# allows to create and verify hashed passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# creates a JWT token in regard of the time set by access token expire minutes
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=TOKEN_EXPIRATION))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# fetch the payload from the token and return the current user associated with it
def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/users/login"))):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin")

        if username is None:
            raise HTTPException(INVALID_TOKEN_EX)

        return {"username": username, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(INVALID_TOKEN_EX)


def admin_required(current_user=Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(ADMIN_REQUIRED_EX)
    return current_user

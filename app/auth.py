from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = "verysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# allows to create and verify hashed passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# returns the hashed version of the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# verifies that the provided password matches the hashed password
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# creates a JWT token in regard of the time set by access token expire minutes
def create_access_token(data: dict, expires_delta: timedelta | None = None):

    # avoid modifying the original data
    to_encode = data.copy() 

    # set expiration time
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # add expiration to the payload
    to_encode.update({"exp": expire}) 

    # encode the token with the secret key and algorithm
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/users/login"))):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin")

        # after fetching the content of the payload, defining username and admin status
        # the token is invalid if username doesn't exist.
        if username is None: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return {"username": username, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
def admin_required(current_user=Depends(get_current_user)):
    if not current_user.get("is_admin", False): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from jose import jwt
from ..constants import SECRET_KEY, ALGORITHM, TOKEN_EXPIRATION_MINS


# allows to create and verify hashed passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# creates a JWT token in regard of the time set by access token expire minutes
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=TOKEN_EXPIRATION_MINS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
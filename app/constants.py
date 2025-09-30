from fastapi import HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRATION_MINS = int(os.getenv("TOKEN_EXPIRATION_MINUTES", 30))


# === Predefined exceptions ===
# 400
USERNAME_TAKEN_EX = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Username already taken"
)

INVALID_CREDENTIALS_EX = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Username already taken"
)

# 401
INVALID_TOKEN_EX = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token"
)

# 403
ADMIN_REQUIRED_EX = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Admin privileges required"
)

DELETING_SELF_EX = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden, admin cannot delete self"
)

DELETING_TASK_EX = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden, not allowed to delete this task"
)

# 404
USER_NOT_FOUND_EX = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)

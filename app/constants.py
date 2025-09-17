from fastapi import HTTPException, status

# Security settings
SECRET_KEY = "verysecretkey"
ALGORITHM = "HS256"
TOKEN_EXPIRATION = 30

# === Predefined exceptions ===
#400
USERNAME_TAKEN_EX = HTTPException(
    status_code=400, 
    detail="Username already taken"
)

INVALID_CREDENTIALS_EX = HTTPException(
    status_code=400, 
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

#404
USER_NOT_FOUND_EX = HTTPException(
    status_code=404,
    detail="User not found"
)

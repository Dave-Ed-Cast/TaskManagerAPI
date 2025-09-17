from fastapi import HTTPException, status

# Security settings
SECRET_KEY = "verysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# === Predefined exceptions ===
# 401
INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token"
)

# 403
ADMIN_REQUIRED_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Admin privileges required"
)

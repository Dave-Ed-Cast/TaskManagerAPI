from .database import get_db
from .auth import hash_password, create_access_token
from fastapi import HTTPException
from datetime import datetime

import sqlite3

def create_user(username: str, password: str, is_admin: bool = False):
    from .crud import get_user  # avoid circular import

    # 1. Check if user already exists
    if get_user(username):
        raise HTTPException(status_code=409, detail="Username already exists")

    hashed_pw = hash_password(password)

    # 2. Insert into database
    try:
        with get_db() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password, is_admin) VALUES (?, ?, ?)",
                (username, hashed_pw, int(is_admin))
            )
            connection.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Generate JWT token
    access_token = create_access_token({
        "sub": username,
        "user_id": user_id,
        "is_admin": is_admin
    })

    # 4. Return JSON for frontend
    return {
        "username": username,
        "is_admin": is_admin,
        "created_at": datetime.utcnow().isoformat(),
        "access_token": access_token,
        "token_type": "bearer"
    }


def delete_user(username: str) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        connection.commit()
        return cursor.rowcount > 0  # true if deleted


def get_user(username: str):
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, username, hashed_password, is_admin FROM users WHERE username=?", (username,))
        return cursor.fetchone()


def create_task(title: str, description: str, owner_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, description, owner_id) VALUES (?, ?, ?)",
                       (title, description, owner_id))
        conn.commit()


def get_tasks(owner_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE owner_id=?", (owner_id,))
        return cursor.fetchall()


def update_user_role(username: str, is_admin: bool) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET is_admin=? WHERE username=?", (int(is_admin), username))
        connection.commit()
        return cursor.rowcount > 0  # true if updated


def update_user_password(username: str, new_password: str) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET hashed_password=? WHERE username=?",
                       (hash_password(new_password), username))
        connection.commit()
        return cursor.rowcount > 0  # true if updated

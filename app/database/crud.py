from .database import get_db
from .auth import hash_password, create_access_token
from ..constants import USERNAME_TAKEN_EX
from fastapi import HTTPException
from datetime import datetime, timezone

import sqlite3

# ==== C in the crud acronym ====
def create_user(username: str, password: str, is_admin: bool = False):
    from .crud import get_user  # avoid circular import

    if get_user(username):
        raise HTTPException(USERNAME_TAKEN_EX)

    hashed_pw = hash_password(password)

    try:
        with get_db() as connection:
            cursor = connection.cursor()
            create_query = "INSERT INTO users (username, hashed_password, is_admin) VALUES (?, ?, ?)"
            cursor.execute(create_query, (username, hashed_pw, int(is_admin)))
            connection.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    access_token = create_access_token({
        "sub": username,
        "user_id": user_id,
        "is_admin": is_admin
    })

    return {
        "username": username,
        "is_admin": is_admin,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "access_token": access_token,
        "token_type": "bearer"
    }


def create_task(title: str, description: str, owner_id: int, is_shared: bool = False):
    with get_db() as connection:
        cursor = connection.cursor()
        create_query = "INSERT INTO tasks (title, description, owner_id, is_shared) VALUES (?, ?, ?, ?)"
        cursor.execute(create_query, (title, description, owner_id, int(is_shared)))
        connection.commit()


# ==== R in the crud acronym ====
def get_user(username: str):
    with get_db() as connection:
        cursor = connection.cursor()
        get_query = "SELECT id, username, hashed_password, is_admin FROM users WHERE username=?"
        cursor.execute(get_query, (username,))
        return cursor.fetchone()


# Fetch the user, either admin or user and filter the output
def get_tasks_for_user(user_tuple: tuple):
    user = {
        "id": user_tuple[0],
        "username": user_tuple[1],
        "is_admin": bool(user_tuple[3])
    }

    with get_db() as connection:
        cursor = connection.cursor()
        if user['is_admin']:
            # Admins see their own tasks plus any shared tasks
            query = "SELECT * FROM tasks WHERE owner_id=? OR is_shared=1"
            cursor.execute(query, (user['id'],))
        else:
            # Regular users see only their own tasks
            query = "SELECT * FROM tasks WHERE owner_id=?"
            cursor.execute(query, (user['id'],))
        
        return cursor.fetchall()
    

# ==== U in the crud acronym ====
def update_user_role(username: str, is_admin: bool) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        update_query = "UPDATE users SET is_admin=? WHERE username=?"
        cursor.execute(update_query, (int(is_admin), username))
        connection.commit()
        return cursor.rowcount > 0  # true if updated


def update_user_password(username: str, new_password: str) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        update_query = "UPDATE users SET hashed_password=? WHERE username=?"
        cursor.execute(update_query, (hash_password(new_password), username))
        connection.commit()
        return cursor.rowcount > 0  # true if updated


# ==== D in the crud acronym ====
def delete_user(username: str) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        delete_query = "DELETE FROM users WHERE username=?"
        cursor.execute(delete_query, (username,))
        connection.commit()
        return cursor.rowcount > 0  # true if deleted

from .database import get_db
from .auth import hash_password, create_access_token
from ..constants import USERNAME_TAKEN_EX
from .utility import _row_to_user_dict, _row_to_task_dict
from fastapi import HTTPException
from datetime import datetime, timezone
import sqlite3

# ==== C in the crud acronym ====
def create_user(username: str, password: str, is_admin: bool = False):
    hashed_pw = hash_password(password)

    try:
        with get_db() as connection:
            cursor = connection.cursor()
            create_query = """
                INSERT INTO users (
                    username, 
                    hashed_password, 
                    is_admin
                )
                VALUES (?, ?, ?)
            """
            cursor.execute(create_query, (username, hashed_pw, int(is_admin)))
            connection.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(USERNAME_TAKEN_EX)

    access_token = create_access_token({
        "sub": username,
        "user_id": user_id,
        "is_admin": is_admin
    })

    return {
        "id": user_id,
        "username": username,
        "is_admin": bool(is_admin),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "access_token": access_token,
        "token_type": "bearer"
    }


def create_task(title: str, description: str, owner_id: int, is_shared: bool = False):
    with get_db() as connection:
        cursor = connection.cursor()
        create_query = """
            INSERT INTO tasks (
                title, 
                description, 
                owner_id, 
                is_shared
            )
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(create_query, (title, description, owner_id, int(is_shared)))
        connection.commit()


# ==== R in the crud acronym ====
def get_user(username: str):
    with get_db() as connection:
        cursor = connection.cursor()
        get_query = """
            SELECT 
                id, 
                username, 
                hashed_password, 
                is_admin 
            FROM users 
            WHERE username = ?
        """
        cursor.execute(get_query, (username,))
        row = cursor.fetchone()
        return _row_to_user_dict(row)


def get_tasks_for_user(user: dict):
    user_id = user["id"]
    is_admin_user = user["is_admin"]

    with get_db() as connection:
        cursor = connection.cursor()

        if is_admin_user:
            cursor.execute("SELECT * FROM tasks WHERE owner_id=?", (user_id,))
            personal_tasks = cursor.fetchall()

            cursor.execute("SELECT * FROM tasks WHERE is_shared=1")
            shared_tasks = cursor.fetchall()

            rows = personal_tasks + shared_tasks
            rows = list({task["id"]: task for task in rows}.values())  # remove duplicates if any
        else: 
            cursor.execute("SELECT * FROM tasks WHERE owner_id=?", (user_id,))
            rows = cursor.fetchall()

        return [_row_to_task_dict(r) for r in rows]


# ==== U in the crud acronym ====
def update_user_role(username: str, is_admin: bool) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        update_query = """
            UPDATE users 
            SET is_admin = ? 
            WHERE username = ?
        """
        cursor.execute(update_query, (int(is_admin), username))
        connection.commit()
        return cursor.rowcount > 0  # true if updated


def update_user_password(username: str, new_password: str) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        update_query = """
            UPDATE users 
            SET hashed_password = ? 
            WHERE username = ?
        """
        cursor.execute(update_query, (hash_password(new_password), username))
        connection.commit()
        return cursor.rowcount > 0  # true if updated


# ==== D in the crud acronym ====
def delete_user(username: str) -> bool:
    with get_db() as connection:
        cursor = connection.cursor()
        delete_query = """
            DELETE FROM users 
            WHERE username = ?
        """
        cursor.execute(delete_query, (username,))
        connection.commit()
        return cursor.rowcount > 0  # true if deleted

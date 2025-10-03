from .database import get_db
from ..constants import USERNAME_TAKEN_EX
from .auth import hash_password, create_access_token
from ..constants import USERNAME_TAKEN_EX
from .utility import _row_to_user_dict, _row_to_task_dict
from fastapi import HTTPException
from datetime import datetime, timezone

# ==== C in the crud acronym ====
async def create_user(username: str, password: str, is_admin: bool = False):
    hashed_pw = hash_password(password)

    try:
        async with get_db() as connection:
            cursor = await connection.execute(
                """
                INSERT INTO users (username, hashed_password, is_admin)
                VALUES (?, ?, ?)
                """,
                (username, hashed_pw, int(is_admin))
            )
            await connection.commit()
            user_id = cursor.lastrowid
    except Exception as e:
        # SQLite raises IntegrityError for duplicates
        if 'UNIQUE constraint failed' in str(e):
            raise HTTPException(USERNAME_TAKEN_EX)
        raise

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


async def create_task(title: str, description: str, owner_id: int, is_shared: bool = False):
    async with get_db() as connection:
        cursor = await connection.execute(
            """
            INSERT INTO tasks (title, description, owner_id, is_shared)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, owner_id, int(is_shared))
        )
        await connection.commit()
        return cursor.lastrowid


# ==== R in the crud acronym ====
async def get_user(username: str):
    async with get_db() as connection:
        cursor = await connection.execute(
            """
            SELECT id, username, hashed_password, is_admin
            FROM users
            WHERE username = ?
            """,
            (username,)
        )
        row = await cursor.fetchone()
        return _row_to_user_dict(row)


async def get_tasks_for_user(user: dict):
    user_id = user["id"]
    is_admin_user = user["is_admin"]

    async with get_db() as connection:
        if is_admin_user:
            cursor = await connection.execute(
                "SELECT * FROM tasks WHERE owner_id=? OR is_shared=1",
                (user_id,)
            )
            rows = await cursor.fetchall()
            # remove duplicates if any (just in case)
            rows = list({task["id"]: task for task in rows}.values())
        else:
            cursor = await connection.execute(
                "SELECT * FROM tasks WHERE owner_id=?",
                (user_id,)
            )
            rows = await cursor.fetchall()

        return [_row_to_task_dict(r) for r in rows]


async def get_all_tasks():
    async with get_db() as connection:
        cursor = await connection.execute("SELECT * FROM tasks")
        rows = await cursor.fetchall()
        return rows


# ==== U in the crud acronym ====
async def update_user_role(username: str, is_admin: bool) -> bool:
    async with get_db() as connection:
        cursor = await connection.execute(
            "UPDATE users SET is_admin = ? WHERE username = ?",
            (int(is_admin), username)
        )
        await connection.commit()
        return cursor.rowcount > 0


async def update_user_password(username: str, new_password: str) -> bool:
    async with get_db() as connection:
        cursor = await connection.execute(
            "UPDATE users SET hashed_password = ? WHERE username = ?",
            (hash_password(new_password), username)
        )
        await connection.commit()
        return cursor.rowcount > 0


# ==== D in the crud acronym ====
async def delete_user(username: str) -> bool:
    async with get_db() as connection:
        cursor = await connection.execute(
            "DELETE FROM users WHERE username = ?",
            (username,)
        )
        await connection.commit()
        return cursor.rowcount > 0


async def delete_task(task_id: int, user_id: int, is_admin: bool) -> bool:
    async with get_db() as connection:
        cursor = await connection.execute(
            "DELETE FROM tasks WHERE id = ? AND (owner_id = ? OR ? = 1)",
            (task_id, user_id, int(is_admin))
        )
        await connection.commit()
        return cursor.rowcount > 0

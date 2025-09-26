import sqlite3


def _row_to_user_dict(row: sqlite3.Row | None):
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "hashed_password": row["hashed_password"],
        "is_admin": bool(row["is_admin"])
    }

def _row_to_task_dict(row: sqlite3.Row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "done": bool(row["done"]),
        "owner_id": row["owner_id"],
        "is_shared": bool(row["is_shared"]),
    }
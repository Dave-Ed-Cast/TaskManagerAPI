import sqlite3
from contextlib import contextmanager
from typing import Iterator

DB_NAME = "tasks.db"


def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0
    )
    """)
    # Tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        done BOOLEAN DEFAULT 0,
        owner_id INTEGER,
        is_shared BOOLEAN DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE SET NULL
    )
    """)
    # Add indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_owner_id ON tasks(owner_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_is_shared ON tasks(is_shared)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_owner_shared ON tasks(owner_id, is_shared)")
    connection.commit()
    connection.close()


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    # Each request/context gets its own connection.
    connection = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    # Provide row access by column name
    connection.row_factory = sqlite3.Row
    # Enforce foreign keys on every connection
    connection.execute("PRAGMA foreign_keys = ON;")
    try:
        yield connection
    finally:
        connection.close()

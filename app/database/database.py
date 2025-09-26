import sqlite3
from contextlib import contextmanager

DB_NAME = "tasks.db"

def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
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
        FOREIGN KEY(owner_id) REFERENCES users(id)
    )
    """)
    connection.commit()
    connection.close()

@contextmanager
def get_db():
    connection = sqlite3.connect(DB_NAME)
    
    try: yield connection
    finally: connection.close()

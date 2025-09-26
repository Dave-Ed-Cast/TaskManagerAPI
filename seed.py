import sqlite3
import os

#this is temporary for creating tasks
DB_FILE = "tasks.db"

sample_tasks = [
    # Tasks for Admin davide
    ("task title", "task detail", 3),
    
    # Tasks for User rico
    ("task title", "task detail", 4)
]

def seed_tasks():
    """Connects to the database, deletes all existing tasks, and inserts the sample tasks."""
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        print("Please run the main application first to initialize the database.")
        return

    try:
        with sqlite3.connect(DB_FILE) as connection:
            cursor = connection.cursor()
            """
            # Delete all existing tasks from the table first
            print("Deleting all existing tasks...")
            cursor.execute("DELETE FROM tasks")
            print("Old tasks deleted.")
            """
            # Insert the new sample tasks
            print("Seeding new tasks...")
            cursor.executemany(
                "INSERT INTO tasks (title, description, owner_id) VALUES (?, ?, ?)",
                sample_tasks
            )
            connection.commit()
            print(f"Successfully inserted {len(sample_tasks)} new tasks into the database.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    seed_tasks()
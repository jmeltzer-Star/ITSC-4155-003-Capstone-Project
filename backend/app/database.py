import sqlite3
from flask import current_app


# Purpose:
# This file sets up and manages the SQLite database schema


def get_connection():
    # Establish SQLite connection
    db_name = current_app.config.get("DB_NAME", "tasks.db")
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------------
    # Create table (fresh installs)
    # -------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_date TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL DEFAULT 60,
        effort_level TEXT NOT NULL DEFAULT 'Medium',
        start_after TEXT,
        category TEXT NOT NULL DEFAULT 'General',
        description TEXT,
        notes TEXT
    )
    """)

    # -------------------------------
    # Migration (existing databases)
    # -------------------------------
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [col[1] for col in cursor.fetchall()]

    if "start_after" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN start_after TEXT")

    if "description" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN description TEXT")

    if "notes" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN notes TEXT")

    conn.commit()
    conn.close()
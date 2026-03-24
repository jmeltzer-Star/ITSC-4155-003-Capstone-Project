import sqlite3
from flask import current_app



#Purpose of Database.py: We use SQLLite as Our DataBase | This File is Setting up Our Database in Terms of the Query Format | These are then Used For All Our Backend Loigc 


#this is the Method Which Establishes the Connection 
def get_connection():
    #THis is Our SQite Connection, Bringing in Each Row at a Time
    db_name = current_app.config.get("DB_NAME", "tasks.db")
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

#This is How we update our DB, This is our Our Initial Query Which we Can Then Update Later 
def init_db():
    conn = get_connection()
    #Cursor is apart of SQLite for How we Initliaze + Update Our DataBase
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

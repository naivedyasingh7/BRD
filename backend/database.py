import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brd_history.db")

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            raw_input TEXT,
            cleaned_input TEXT,
            english_brd TEXT,
            localized_brd TEXT,
            language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_brd(project_name: str, raw_input: str, cleaned_input: str, english_brd: str, localized_brd: str, language: str) -> int:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO brds (project_name, raw_input, cleaned_input, english_brd, localized_brd, language)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (project_name, raw_input, cleaned_input, english_brd, localized_brd, language))
    brd_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return brd_id

def get_all_brds():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, language, created_at FROM brds ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_brd_by_id(brd_id: int):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brds WHERE id = ?", (brd_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Initialize on import
init_db()

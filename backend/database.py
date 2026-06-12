import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brd_history.db")


def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
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


def save_brd(project_name: str, raw_input: str, cleaned_input: str, english_brd: str, localized_brd: str, language: str) -> int:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO brds (project_name, raw_input, cleaned_input, english_brd, localized_brd, language) VALUES (?, ?, ?, ?, ?, ?)",
            (project_name, raw_input, cleaned_input, english_brd, localized_brd, language)
        )
        conn.commit()
        return cursor.lastrowid


def get_all_brds():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT id, project_name, language, created_at FROM brds ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_brd_by_id(brd_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM brds WHERE id = ?", (brd_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


init_db()

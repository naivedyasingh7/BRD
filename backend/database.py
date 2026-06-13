import sqlite3
import os
import json
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brd_history.db")
logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    logger.info("Initializing database and applying schema...")
    with get_db_connection() as conn:
        # Enable WAL mode for concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        
        # Projects metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT DEFAULT 'General',
                icon TEXT DEFAULT 'description',
                language TEXT DEFAULT 'English',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # BRD documents (versioned)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                version TEXT NOT NULL,
                raw_input TEXT,
                cleaned_input TEXT,
                english_brd TEXT,
                localized_brd TEXT,
                language TEXT,
                state_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Clarifications history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clarifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Audit trail for explainable AI / agent trace logging
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                request_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                agent_role TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                duration_seconds REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # If legacy data exists in a 'brds' table without project_id, migrate it.
        # Check if project_id exists in brds table
        cursor = conn.execute("PRAGMA table_info(brds)")
        columns = [row[1] for row in cursor.fetchall()]
        if "project_name" in columns:
            # This is a legacy table! Let's rename it and migrate.
            logger.info("Legacy table detected. Performing migration...")
            conn.execute("ALTER TABLE brds RENAME TO legacy_brds;")
            
            # Recreate tables as per new schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS brds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    version TEXT NOT NULL,
                    raw_input TEXT,
                    cleaned_input TEXT,
                    english_brd TEXT,
                    localized_brd TEXT,
                    language TEXT,
                    state_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # Transfer data from legacy_brds to new schema
            legacy_cursor = conn.execute("SELECT * FROM legacy_brds")
            for row in legacy_cursor.fetchall():
                p_name = row["project_name"] or "Legacy Project"
                lang = row["language"] or "English"
                
                # Insert project
                conn.execute(
                    "INSERT OR IGNORE INTO projects (name, language) VALUES (?, ?)",
                    (p_name, lang)
                )
                p_row = conn.execute("SELECT id FROM projects WHERE name = ?", (p_name,)).fetchone()
                p_id = p_row["id"]
                
                # Insert BRD as version 1.0.0
                conn.execute("""
                    INSERT INTO brds (project_id, version, raw_input, cleaned_input, english_brd, localized_brd, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (p_id, "v1.0.0", row["raw_input"], row["cleaned_input"], row["english_brd"], row["localized_brd"], lang))
            
            # Drop legacy table
            conn.execute("DROP TABLE legacy_brds;")
            logger.info("Migration completed successfully.")
            
        conn.commit()


def save_brd(project_name: str, raw_input: str, cleaned_input: str, english_brd: str, localized_brd: str, language: str, state_json: Optional[str] = None) -> int:
    """
    Maintains legacy signature while linking to versioned tables.
    Increments version number if saving to an existing project name.
    """
    with get_db_connection() as conn:
        # 1. Get or create project
        conn.execute(
            "INSERT OR IGNORE INTO projects (name, language) VALUES (?, ?)",
            (project_name, language)
        )
        p_row = conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,)).fetchone()
        project_id = p_row["id"]
        
        # 2. Determine next version number
        v_row = conn.execute(
            "SELECT version FROM brds WHERE project_id = ? ORDER BY id DESC LIMIT 1",
            (project_id,)
        )
        last_version = v_row.fetchone()
        if last_version:
            # Parse version string vX.Y.Z
            v_str = last_version["version"]
            if v_str.startswith("v"):
                try:
                    parts = v_str[1:].split(".")
                    major = int(parts[0])
                    minor = int(parts[1]) if len(parts) > 1 else 0
                    # Increment minor version
                    new_version = f"v{major}.{minor + 1}.0"
                except Exception:
                    new_version = "v1.1.0"
            else:
                new_version = "v1.1.0"
        else:
            new_version = "v1.0.0"
            
        # 3. Save BRD version
        cursor = conn.execute("""
            INSERT INTO brds (project_id, version, raw_input, cleaned_input, english_brd, localized_brd, language, state_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, new_version, raw_input, cleaned_input, english_brd, localized_brd, language, state_json))
        conn.commit()
        return cursor.lastrowid


def save_clarification(project_name: str, question: str, answer: str):
    with get_db_connection() as conn:
        p_row = conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,)).fetchone()
        if p_row:
            conn.execute(
                "INSERT INTO clarifications (project_id, question, answer) VALUES (?, ?, ?)",
                (p_row["id"], question, answer)
            )
            conn.commit()


def save_audit_log(project_name: str, request_id: str, step_name: str, agent_role: str, input_data: str, output_data: str, duration: float, status: str):
    with get_db_connection() as conn:
        p_row = conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,)).fetchone()
        if p_row:
            conn.execute("""
                INSERT INTO audit_trail (project_id, request_id, step_name, agent_role, input_data, output_data, duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (p_row["id"], request_id, step_name, agent_role, input_data, output_data, duration, status))
            conn.commit()


def get_all_brds() -> List[Dict[str, Any]]:
    """
    Returns list of BRDs compatible with the main.py API endpoint.
    Retrieves the latest version of each project.
    """
    with get_db_connection() as conn:
        # Subquery to select the latest BRD version per project
        cursor = conn.execute("""
            SELECT b.id, p.name as project_name, p.language, b.created_at
            FROM projects p
            JOIN brds b ON p.id = b.project_id
            WHERE b.id = (
                SELECT MAX(b2.id)
                FROM brds b2
                WHERE b2.project_id = p.id
            )
            ORDER BY b.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_brd_by_id(brd_id: int) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT b.id, p.name as project_name, b.raw_input, b.cleaned_input, b.english_brd, b.localized_brd, b.language, b.version, b.state_json, b.created_at
            FROM brds b
            JOIN projects p ON b.project_id = p.id
            WHERE b.id = ?
        """, (brd_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_project_history(project_name: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT b.id, b.version, b.english_brd, b.localized_brd, b.created_at
            FROM brds b
            JOIN projects p ON b.project_id = p.id
            WHERE p.name = ?
            ORDER BY b.id DESC
        """, (project_name,))
        return [dict(row) for row in cursor.fetchall()]


def get_audit_trail(project_name: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT a.step_name, a.agent_role, a.input_data, a.output_data, a.duration_seconds, a.status, a.created_at
            FROM audit_trail a
            JOIN projects p ON a.project_id = p.id
            WHERE p.name = ?
            ORDER BY a.created_at ASC
        """, (project_name,))
        return [dict(row) for row in cursor.fetchall()]


# Initialize tables when module is imported
init_db()

import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brd_history.db")

def init_db():
<<<<<<< Updated upstream
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
=======
    logger.info("Initializing database and applying schema...")
    with get_db_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute()
        conn.execute()
        conn.execute()
        conn.execute()
        cursor = conn.execute("PRAGMA table_info(brds)")
        columns = [row[1] for row in cursor.fetchall()]
        if "project_name" in columns:
            logger.info("Legacy table detected. Performing migration...")
            conn.execute("ALTER TABLE brds RENAME TO legacy_brds;")
            conn.execute()
            legacy_cursor = conn.execute("SELECT * FROM legacy_brds")
            for row in legacy_cursor.fetchall():
                p_name = row["project_name"] or "Legacy Project"
                lang = row["language"] or "English"
                conn.execute(
                    "INSERT OR IGNORE INTO projects (name, language) VALUES (?, ?)",
                    (p_name, lang)
                )
                p_row = conn.execute("SELECT id FROM projects WHERE name = ?", (p_name,)).fetchone()
                p_id = p_row["id"]
                conn.execute(, (p_id, "v1.0.0", row["raw_input"], row["cleaned_input"], row["english_brd"], row["localized_brd"], lang))
            conn.execute("DROP TABLE legacy_brds;")
            logger.info("Migration completed successfully.")
            
        conn.commit()


def save_brd(project_name: str, raw_input: str, cleaned_input: str, english_brd: str, localized_brd: str, language: str, mermaid_flowchart: str = "", state_json: Optional[str] = None) -> int:
    
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO projects (name, language) VALUES (?, ?)",
            (project_name, language)
        )
        p_row = conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,)).fetchone()
        project_id = p_row["id"]
        v_row = conn.execute(
            "SELECT version FROM brds WHERE project_id = ? ORDER BY id DESC LIMIT 1",
            (project_id,)
        )
        last_version = v_row.fetchone()
        if last_version:
            v_str = last_version["version"]
            if v_str.startswith("v"):
                try:
                    parts = v_str[1:].split(".")
                    major = int(parts[0])
                    minor = int(parts[1]) if len(parts) > 1 else 0
                    new_version = f"v{major}.{minor + 1}.0"
                except Exception:
                    new_version = "v1.1.0"
            else:
                new_version = "v1.1.0"
        else:
            new_version = "v1.0.0"
        cursor = conn.execute(, (project_id, new_version, raw_input, cleaned_input, english_brd, localized_brd, language, mermaid_flowchart, state_json))
        conn.commit()
        return cursor.lastrowid
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
# Initialize on import
=======
def save_audit_log(project_name: str, request_id: str, step_name: str, agent_role: str, input_data: str, output_data: str, duration: float, status: str):
    with get_db_connection() as conn:
        p_row = conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,)).fetchone()
        if p_row:
            conn.execute(, (p_row["id"], request_id, step_name, agent_role, input_data, output_data, duration, status))
            conn.commit()


def get_all_brds() -> List[Dict[str, Any]]:
    
    with get_db_connection() as conn:
        cursor = conn.execute()
        return [dict(row) for row in cursor.fetchall()]


def get_brd_by_id(brd_id: int) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute(, (brd_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_project_history(project_name: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute(, (project_name,))
        return [dict(row) for row in cursor.fetchall()]


def get_audit_trail(project_name: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute(, (project_name,))
        return [dict(row) for row in cursor.fetchall()]
>>>>>>> Stashed changes
init_db()

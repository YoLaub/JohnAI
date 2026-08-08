import sqlite3
import os
import json
import uuid
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "data", "johnai_memory.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """Initialize central SQLite memory database for multi-device sync"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for full conversation history across all devices (Mac, Windows, Android)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_type TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            model_used TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table for long-term memory facts & user preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact_key TEXT UNIQUE NOT NULL,
            fact_value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Categories used to organize conversation_history entries (thoughts/notes).
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL COLLATE NOCASE
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        default_categories = ["Famille", "R&D", "Évolution personnelle", "Philo", "Projet"]
        cursor.executemany(
            "INSERT INTO categories (name) VALUES (?)",
            [(name,) for name in default_categories]
        )

    # Migration: conversation_history predates the category column.
    cursor.execute("PRAGMA table_info(conversation_history)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "category" not in existing_columns:
        cursor.execute("ALTER TABLE conversation_history ADD COLUMN category TEXT")

    conn.commit()
    conn.close()
    print(f"Base de données mémoire centralisée initialisée sur: {DB_PATH}")

def save_message(device_type: str, role: str, content: str, model_used: str = None, category: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversation_history (device_type, role, content, model_used, category) VALUES (?, ?, ?, ?, ?)",
        (device_type, role, content, model_used, category)
    )
    conn.commit()
    conn.close()

def get_recent_history(limit: int = 20):
    """Role + content only — this feeds the LLM's context window, keep it minimal."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    # Reverse to keep chronological order
    history = []
    for role, content in reversed(rows):
        history.append({"role": role, "content": content})
    return history

def get_message_history(limit: int = 50):
    """Full rows (id, category included) for the dashboard/journal UI."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, role, content, category FROM conversation_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    history = []
    for id_, role, content, category in reversed(rows):
        history.append({"id": id_, "role": role, "content": content, "category": category})
    return history

def list_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories ORDER BY name COLLATE NOCASE ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def create_category(name: str) -> str:
    name = name.strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return name

def set_message_category(message_id: int, category: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversation_history SET category = ? WHERE id = ?",
        (category, message_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def set_message_content(message_id: int, content: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversation_history SET content = ? WHERE id = ?",
        (content, message_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def set_category_for_last_message(category: str, role: str = "user") -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM conversation_history WHERE role = ? ORDER BY id DESC LIMIT 1",
        (role,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    cursor.execute(
        "UPDATE conversation_history SET category = ? WHERE id = ?",
        (category, row[0])
    )
    conn.commit()
    conn.close()
    return True

def add_memory_fact(value: str) -> str:
    """Store a new free-form memorized fact (not an update — always a new row)."""
    fact_key = uuid.uuid4().hex
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO long_term_memory (fact_key, fact_value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (fact_key, value)
    )
    conn.commit()
    conn.close()
    return fact_key


def get_all_memory_facts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT fact_key, fact_value FROM long_term_memory ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"fact_key": key, "fact_value": value} for key, value in rows]


def delete_memory_facts_matching(query: str):
    """Delete every fact whose value contains `query` (case-insensitive). Returns the deleted values."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fact_value FROM long_term_memory WHERE fact_value LIKE ? COLLATE NOCASE",
        (f"%{query}%",)
    )
    deleted_values = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        "DELETE FROM long_term_memory WHERE fact_value LIKE ? COLLATE NOCASE",
        (f"%{query}%",)
    )
    conn.commit()
    conn.close()
    return deleted_values


def save_memory_fact(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO long_term_memory (fact_key, fact_value, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(fact_key) DO UPDATE SET fact_value=excluded.fact_value, updated_at=CURRENT_TIMESTAMP
        """,
        (key, value)
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

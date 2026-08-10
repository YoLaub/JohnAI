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

    # Undirected links between two notes ("what's connected to what, and since
    # when") — from_id/to_id order is just insertion order, not semantics.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id INTEGER NOT NULL,
            to_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

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
    """id + role + content — id is dropped before this feeds the LLM (see
    main.py) and is only used server-side to pull in linked notes (note_links)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, role, content FROM conversation_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    # Reverse to keep chronological order
    history = []
    for id_, role, content in reversed(rows):
        history.append({"id": id_, "role": role, "content": content})
    return history

def get_linked_notes_context(message_ids):
    """Notes linked (note_links) to any of the given message ids, deduped by
    target note. Not filtered to "outside the window" — the point is the
    explicit *connection* (and since when), which plain recent-history text
    doesn't convey even if the linked note's raw content is already visible.
    created_at is the link's own timestamp (since when they're connected),
    not the note's own timestamp."""
    if not message_ids:
        return []

    ids = list(message_ids)
    placeholders = ",".join("?" for _ in ids)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT nl.id,
               CASE WHEN nl.from_id IN ({placeholders}) THEN nl.to_id ELSE nl.from_id END AS other_id,
               nl.created_at, ch.content
        FROM note_links nl
        JOIN conversation_history ch
          ON ch.id = CASE WHEN nl.from_id IN ({placeholders}) THEN nl.to_id ELSE nl.from_id END
        WHERE nl.from_id IN ({placeholders}) OR nl.to_id IN ({placeholders})
    """, ids * 4)
    rows = cursor.fetchall()
    conn.close()

    seen = set()
    context = []
    for _link_id, other_id, created_at, content in rows:
        if other_id in seen:
            continue
        seen.add(other_id)
        context.append({"message_id": other_id, "content": content, "created_at": created_at})
    return context

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

def get_messages_by_category(category: str, limit: int = 100):
    """User notes in a given category — case-insensitive, matching how
    categories.name itself is compared (COLLATE NOCASE) everywhere else."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, content, timestamp FROM conversation_history
           WHERE role = 'user' AND category = ? COLLATE NOCASE
           ORDER BY id DESC LIMIT ?""",
        (category, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": id_, "content": content, "created_at": created_at} for id_, content, created_at in rows]

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

def delete_message(message_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM note_links WHERE from_id = ? OR to_id = ?",
        (message_id, message_id)
    )
    cursor.execute("DELETE FROM conversation_history WHERE id = ?", (message_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def create_note_link(from_id: int, to_id: int) -> int | None:
    """Undirected: idempotent regardless of which side is passed as from/to."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM note_links WHERE (from_id = ? AND to_id = ?) OR (from_id = ? AND to_id = ?)",
        (from_id, to_id, to_id, from_id)
    )
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    cursor.execute("SELECT 1 FROM conversation_history WHERE id = ?", (to_id,))
    if not cursor.fetchone():
        conn.close()
        return None

    cursor.execute("INSERT INTO note_links (from_id, to_id) VALUES (?, ?)", (from_id, to_id))
    link_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return link_id

def get_links_for_message(message_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nl.id, nl.created_at,
               CASE WHEN nl.from_id = ? THEN nl.to_id ELSE nl.from_id END AS other_id,
               ch.role, ch.content, ch.category
        FROM note_links nl
        JOIN conversation_history ch
          ON ch.id = CASE WHEN nl.from_id = ? THEN nl.to_id ELSE nl.from_id END
        WHERE nl.from_id = ? OR nl.to_id = ?
        ORDER BY nl.created_at DESC
    """, (message_id, message_id, message_id, message_id))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "link_id": link_id,
            "created_at": created_at,
            "message_id": other_id,
            "role": role,
            "content": content,
            "category": category,
        }
        for link_id, created_at, other_id, role, content, category in rows
    ]

def delete_note_link(link_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM note_links WHERE id = ?", (link_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_related_notes(message_id: int, max_hops: int = 2):
    """BFS over note_links via a recursive CTE, capped at max_hops — the
    multi-hop view: "everything connected to this note, and how far away".
    Takes the shortest path when a note is reachable more than one way."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        WITH RECURSIVE reachable(id, hops) AS (
            SELECT ?, 0
            UNION
            SELECT CASE WHEN nl.from_id = r.id THEN nl.to_id ELSE nl.from_id END, r.hops + 1
            FROM note_links nl
            JOIN reachable r ON nl.from_id = r.id OR nl.to_id = r.id
            WHERE r.hops < ?
        )
        SELECT r.id, MIN(r.hops) AS hops, ch.content, ch.category
        FROM reachable r
        JOIN conversation_history ch ON ch.id = r.id
        WHERE r.id != ?
        GROUP BY r.id
        ORDER BY hops ASC, r.id ASC
    """, (message_id, max_hops, message_id))
    rows = cursor.fetchall()
    conn.close()

    return [
        {"message_id": id_, "hops": hops, "content": content, "category": category}
        for id_, hops, content, category in rows
    ]

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

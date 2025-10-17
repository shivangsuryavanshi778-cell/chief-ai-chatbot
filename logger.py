"""
logger.py
Zeus AI Chatbot — Conversation Logger
-------------------------------------
• Uses SQLite for secure, local message logging
• Thread-safe for Streamlit
• Supports conversation history, clear, export, and long-term memory save/load
"""

import sqlite3
import os
import json
import errno
from datetime import datetime
from typing import List, Tuple, Optional

# ==========================
# DATABASE CONFIG
# ==========================
DB_FILENAME = os.path.join(os.path.dirname(__file__), "conversations.db")

# ==========================
# SAFE CONNECTION HANDLER
# ==========================
def _get_conn():
    """Create and return a thread-safe SQLite connection."""
    return sqlite3.connect(DB_FILENAME, check_same_thread=False)

# ==========================
# INITIALIZATION
# ==========================
def init_db():
    """Create DB and messages table if they don’t exist."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# ==========================
# WRITE LOG
# ==========================
def log_message(session_id: str, role: str, message: str):
    """Save one message into the database."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (session_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, message[:2000], datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

# ==========================
# READ LOG
# ==========================
def get_history(session_id: str, limit: Optional[int] = None) -> List[Tuple[int, str, str, str]]:
    """Fetch chat history for a session."""
    conn = _get_conn()
    cur = conn.cursor()
    if limit:
        cur.execute(
            "SELECT id, role, message, created_at FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?",
            (session_id, limit)
        )
    else:
        cur.execute(
            "SELECT id, role, message, created_at FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
    rows = cur.fetchall()
    conn.close()
    return rows

# ==========================
# CLEAR HISTORY
# ==========================
def clear_history(session_id: str):
    """Delete all history for a given session."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# ==========================
# EXPORT TO CSV
# ==========================
def export_history_csv(session_id: str, out_path: str):
    """Export a session’s conversation to a CSV file."""
    import csv
    rows = get_history(session_id)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "role", "message", "created_at"])
        for r in rows:
            writer.writerow(r)

# ==========================
# SAVE / LOAD LONG-TERM MEMORY
# ==========================

def save_memory(session_id: str) -> (bool, str):
    """Save chat history to a JSON file for long-term storage."""
    try:
        rows = get_history(session_id)
        if not rows:
            return False, "No conversation found to save."

        mem_dir = os.path.join(os.path.dirname(__file__), "memory_store")
        os.makedirs(mem_dir, exist_ok=True)

        history = [
            {"role": role, "message": msg, "created_at": ts}
            for _, role, msg, ts in rows
        ]

        path = os.path.join(mem_dir, f"memory_{session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        return True, f"Conversation saved successfully ({len(history)} messages)."
    except Exception as e:
        return False, f"Error saving memory: {e}"


def load_memory(session_id: str) -> (bool, str):
    """Load saved chat history from JSON back into the database."""
    try:
        mem_dir = os.path.join(os.path.dirname(__file__), "memory_store")
        path = os.path.join(mem_dir, f"memory_{session_id}.json")

        if not os.path.exists(path):
            return False, "No saved memory found for this user."

        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)

        clear_history(session_id)

        conn = _get_conn()
        cur = conn.cursor()
        for h in history:
            cur.execute(
                "INSERT INTO messages (session_id, role, message, created_at) VALUES (?, ?, ?, ?)",
                (session_id, h["role"], h["message"], h["created_at"])
            )
        conn.commit()
        conn.close()
        return True, f"Loaded {len(history)} messages from saved memory."
    except Exception as e:
        return False, f"Error loading memory: {e}"

"""
logger.py
Chief AI Chatbot — Conversation Logger
-------------------------------------
• Uses SQLite for secure, local message logging
• Thread-safe for Streamlit
• No dependencies on external files
• Supports conversation history, clear, and export
"""

import sqlite3
import os
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
        role TEXT NOT NULL,          -- 'user' or 'assistant'
        message TEXT NOT NULL,
        created_at TEXT NOT NULL     -- ISO timestamp
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

import json

def save_memory(user_id: str):
    """
    Copy the user's last session chat from messages table
    into a permanent JSON file named memory_<user_id>.json
    """
    rows = get_history(user_id)
    if not rows:
        return False

    # Create export folder if it doesn't exist
    mem_dir = os.path.join(os.path.dirname(__file__), "memory_store")
    os.makedirs(mem_dir, exist_ok=True)

    # Prepare data
    history = [{"role": role, "message": msg, "created_at": ts}
               for _, role, msg, ts in rows]

    # Write JSON
    path = os.path.join(mem_dir, f"memory_{user_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return True


def load_memory(user_id: str):
    """
    Load a saved memory_<user_id>.json and reinsert into messages table
    so conversation continues from last saved chat.
    """
    mem_dir = os.path.join(os.path.dirname(__file__), "memory_store")
    path = os.path.join(mem_dir, f"memory_{user_id}.json")

    if not os.path.exists(path):
        return False

    with open(path, "r", encoding="utf-8") as f:
        history = json.load(f)

    # clear current temp history first
    clear_history(user_id)

    conn = _get_conn()
    cur = conn.cursor()
    for h in history:
        cur.execute(
            "INSERT INTO messages (session_id, role, message, created_at) VALUES (?, ?, ?, ?)",
            (user_id, h["role"], h["message"], h["created_at"])
        )
    conn.commit()
    conn.close()
    return True

"""
memory_manager.py
Zeus AI Chatbot — Persistent Memory System with User Login
----------------------------------------------------------
Stores and retrieves user-specific memory files based on username.
"""

import os
import json

# Directory to store each user's memory file
MEM_DIR = os.path.join(os.path.dirname(__file__), "user_memory")
os.makedirs(MEM_DIR, exist_ok=True)

def _memory_path(username: str) -> str:
    """Return the file path for this user's memory file."""
    safe_name = username.replace(" ", "_").lower()
    return os.path.join(MEM_DIR, f"{safe_name}.json")

def load_user_memory(username: str) -> dict:
    """Load stored memory data for the user."""
    path = _memory_path(username)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_memory(username: str, memory_data: dict):
    """Save updated memory to disk."""
    path = _memory_path(username)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)

def clear_user_memory(username: str):
    """Erase the user's memory file completely."""
    path = _memory_path(username)
    if os.path.exists(path):
        os.remove(path)

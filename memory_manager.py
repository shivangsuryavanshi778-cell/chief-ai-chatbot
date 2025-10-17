"""
memory_manager.py
Zeus AI Chatbot — Persistent Memory System
------------------------------------------
Stores and retrieves user-specific memory automatically.
"""

import os
import json

# Directory to store each user's memory file
MEM_DIR = os.path.join(os.path.dirname(__file__), "user_memory")
os.makedirs(MEM_DIR, exist_ok=True)

def _memory_path(user_id: str) -> str:
    """Return the file path for this user's memory file."""
    return os.path.join(MEM_DIR, f"{user_id}.json")

def load_user_memory(user_id: str) -> dict:
    """Load stored memory data for the user."""
    path = _memory_path(user_id)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_memory(user_id: str, memory_data: dict):
    """Save updated memory to disk."""
    path = _memory_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)

def clear_user_memory(user_id: str):
    """Erase the user's memory file completely."""
    path = _memory_path(user_id)
    if os.path.exists(path):
        os.remove(path)

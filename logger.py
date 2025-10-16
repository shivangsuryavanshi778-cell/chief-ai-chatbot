"""
logger.py
- Minimal logging: SQLite storage or CSV fallback
- Stores timestamp, user_id, message, intent, confidence, response
"""

import sqlite3
import time
from auth import LOG_PATH

# Initialize DB
conn = sqlite3.connect(LOG_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    user_id TEXT,
    message TEXT,
    intent TEXT,
    confidence REAL,
    response TEXT
)
""")
conn.commit()

def log_interaction(user_id, message, nlu_result, response_text):
    ts = int(time.time())
    intent = nlu_result.get("intent") if nlu_result else None
    confidence = float(nlu_result.get("confidence", 0.0)) if nlu_result else 0.0
    cursor.execute("""
    INSERT INTO interactions (ts, user_id, message, intent, confidence, response)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (ts, str(user_id), message[:2000], intent, confidence, response_text[:2000]))
    conn.commit()

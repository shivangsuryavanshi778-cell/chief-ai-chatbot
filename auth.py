"""
auth.py
- Loads environment variables and provides auth helpers for webhook verification.
"""

import os
from dotenv import load_dotenv

load_dotenv()

IG_PAGE_ID = os.getenv("IG_PAGE_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_VERIFY_TOKEN = os.getenv("IG_VERIFY_TOKEN")
LLM_API_KEY = os.getenv("LLM_API_KEY")
DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("1", "true", "yes")
LOG_PATH = os.getenv("LOG_PATH", "logs.db")

def verify_webhook_mode(req_args):
    """
    Used to verify webhook (GET verification step).
    IG sends 'hub.mode', 'hub.challenge', 'hub.verify_token'
    """
    mode = req_args.get("hub.mode")
    token = req_args.get("hub.verify_token")
    challenge = req_args.get("hub.challenge")
    if mode and token:
        return mode, token, challenge
    return None, None, None

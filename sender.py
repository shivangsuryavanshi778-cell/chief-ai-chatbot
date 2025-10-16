"""
sender.py
- Functions to send messages via Instagram Graph API with retry and exponential backoff.
- In DEV_MODE, responses are simulated and not sent to IG.
"""

import requests
import time
from auth import IG_ACCESS_TOKEN, DEV_MODE
import logging

IG_API_BASE = "https://graph.facebook.com/v16.0"

def _exponential_backoff(attempt):
    return min(60, (2 ** attempt))

def send_instagram_message(recipient_id: str, message_text: str) -> dict:
    """
    Send a text message to recipient_id. Returns a dict with status and metadata.
    """
    logging.info(f"Sending message to {recipient_id}: {message_text}")
    if DEV_MODE:
        # Simulate a success response for local testing
        return {"status": "simulated", "to": recipient_id, "message": message_text}

    url = f"{IG_API_BASE}/{recipient_id}/messages"
    headers = {"Authorization": f"Bearer {IG_ACCESS_TOKEN}"}
    payload = {"message": {"text": message_text}}

    for attempt in range(5):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            if r.status_code == 200:
                return {"status": "sent", "result": r.json()}
            elif r.status_code == 429:
                backoff = _exponential_backoff(attempt)
                logging.warning(f"Rate limited. Sleeping {backoff}s")
                time.sleep(backoff)
                continue
            else:
                logging.error(f"Send failed: {r.status_code} {r.text}")
                return {"status": "failed", "code": r.status_code, "text": r.text}
        except requests.RequestException as e:
            logging.warning(f"Request exception: {e}. Retrying...")
            time.sleep(_exponential_backoff(attempt))
    return {"status": "failed", "error": "max_retries_exceeded"}

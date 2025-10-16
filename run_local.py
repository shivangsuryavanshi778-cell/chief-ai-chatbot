"""
run_local.py
- Starts the Flask app (app.py). Also contains a simulated message sender for testing.
- Run this in PyCharm run configuration for easy debugging.
"""

import subprocess
import threading
import requests
import time
import json
import os

from app import app  # Flask app
from auth import DEV_MODE

def start_server():
    # Start Flask app (debug mode is set in app.py)
    app.run(port=5000)

def simulate_message(sender_id="test_user_1", text="Hi, what are your hours?"):
    """
    Sends a simulated webhook-like payload to /webhook so you can test flow without IG.
    """
    payload = {
        "entry": [
            {
                "messaging": [
                    {"sender": {"id": sender_id}, "message": {"text": text}}
                ]
            }
        ]
    }
    r = requests.post("http://127.0.0.1:5000/webhook", json=payload)
    try:
        print("Simulate response:", r.status_code, r.json())
    except Exception:
        print("Simulate response text:", r.text)

if __name__ == "__main__":
    # Start Flask server in a thread to allow simulation in same process (useful in PyCharm)
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1.5)  # wait for server to start
    # Simulate a couple messages
    simulate_message(text="Hello")
    simulate_message(text="Can you tell me the pricing?")
    simulate_message(text="I want to track my order #12345")
    print("Simulated messages sent. Check logs or DB.")

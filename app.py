"""
app.py
- Flask webhook receiver + health endpoint
- Receives IG webhook events (messages/comments)
"""
from dotenv import load_dotenv
load_dotenv()
import os


from flask import Flask, request, jsonify
import logging
from auth import verify_webhook_mode, IG_VERIFY_TOKEN, DEV_MODE
from nlu import parse_message
from responder import generate_response
from sender import send_instagram_message
from logger import log_interaction

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "dev_mode": DEV_MODE})

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode, token, challenge = verify_webhook_mode(request.args)
        if mode == "subscribe" and token == IG_VERIFY_TOKEN:
            return challenge, 200
        return "Unauthorized", 403

    payload = request.get_json(force=True)
    # Basic sanitizer: ensure dict and small size
    if not isinstance(payload, dict) or len(str(payload)) > 200000:
        return "Bad Request", 400

    # Handle IG messaging events (simplified)
    events = payload.get("entry", [])
    responses = []
    for entry in events:
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id") or messaging.get("from", {}).get("id")
            text = None
            if "message" in messaging:
                text = messaging["message"].get("text")
            elif "comment" in messaging:
                text = messaging["comment"].get("text")
            if not text:
                continue

            # NLU
            nlu_result = parse_message(text)
            # Response
            response_text = generate_response(text, nlu_result)
            # Log
            log_interaction(sender_id, text, nlu_result, response_text)

            # Send (dev-mode will simulate)
            send_result = send_instagram_message(sender_id, response_text)
            responses.append({"to": sender_id, "sent": send_result})
    return jsonify({"ok": True, "responses": responses})

if __name__ == "__main__":
    app.run(port=5000, debug=True)

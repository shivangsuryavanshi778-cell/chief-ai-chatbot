"""
responder.py
-------------
Handles chatbot response generation logic for ChiefAI.
Now powered by OpenRouter (free GPT-like models) instead of OpenAI billing.

Key Features:
- Contextual replies using OpenRouter GPT models
- Safe fallbacks (offline pseudo-AI replies if API fails)
- Modular and production-ready
"""

import os
import random
import requests

# === ENVIRONMENT SETUP ===
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# === CONFIG ===
MAX_TOKENS = 250
TEMPERATURE = 0.7
DEFAULT_MODEL = "openrouter/gpt-3.5-turbo"  # Change this to another available model if desired

# === FALLBACK RESPONSES (Offline Mode) ===
FALLBACK_IDEAS = [
    "That’s an interesting thought, Chief 👑. Tell me more!",
    "Hmm... I like where this is going. Maybe try something creative?",
    "Good question, Chief — I’d say keep exploring that idea.",
    "I feel you. Maybe take a short break and come back refreshed?",
    "That sounds like something we can solve together, Chief 😎",
    "Not totally sure, but it sounds like you’re onto something smart.",
    "Let’s think about it logically — what’s your first instinct?",
    "Haha, I like your curiosity, Chief. Let’s break this down!"
]


# === PRIMARY LLM CALLER (OPENROUTER) ===
import requests
import os

# === PRIMARY LLM CALLER (OPENROUTER) ===
def _call_llm(prompt: str) -> str:
    """
    Calls OpenRouter's chat-completion endpoint for contextual replies.
    """
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").lower()
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    if LLM_PROVIDER != "openrouter":
        return "(⚠️ No valid LLM provider specified in .env.)"

    if not OPENROUTER_API_KEY:
        return "(⚠️ No OpenRouter API key found in .env file.)"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-3.5-turbo",  # You can use 'mistralai/mistral-7b' or 'openai/gpt-4o-mini'
        "messages": [
            {"role": "system", "content": "You are Chief’s friendly AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        return f"(⚠️ OpenRouter error: {e})"



# === OFFLINE SIMULATED FALLBACK REPLY ===
def _simulate_reply(prompt: str) -> str:
    """
    Simple local AI-style fallback reply when API fails or key is missing.
    Generates natural responses without external calls.
    """
    base = random.choice(FALLBACK_IDEAS)
    if "bored" in prompt.lower():
        base = "Sounds like you need a challenge, Chief 👑. How about learning something new?"
    elif "sad" in prompt.lower():
        base = "Hey, tough times happen — but you’ve got this, Chief. Keep your head high 💪"
    elif "hello" in prompt.lower() or "hi" in prompt.lower():
        base = "Hey Chief 👑! How’s it going today?"
    elif "bye" in prompt.lower():
        base = "Catch you later, Chief! 👋 Stay awesome."
    return base


# === RESPONSE GENERATOR (MAIN LOGIC) ===
def generate_response(user_input: str, nlu_data: dict = None) -> str:
    """
    Generates a reply based on detected intent or LLM fallback.
    :param user_input: Raw message text from user.
    :param nlu_data: Parsed data from NLU (intent, confidence, etc.)
    """
    try:
        # Use detected intent if NLU provided
        if nlu_data and "intent" in nlu_data:
            intent = nlu_data["intent"]
            confidence = nlu_data.get("confidence", 0.0)

            # Handle known intents via templates
            if intent == "greeting":
                return "Hey Chief 👑! How can I assist you today?"
            elif intent == "goodbye":
                return "Take care, Chief! 👋 See you soon."
            elif intent == "thanks":
                return "Always a pleasure to help, Chief 🙌"
            elif intent == "about_bot":
                return "I’m ChiefAI — your personal chatbot created by Shivang Suryavanshi. Ready to assist anytime."

            # If low confidence → use LLM fallback
            if confidence < 0.6:
                return _call_llm(user_input)

        # If no NLU or fallback condition
        return _call_llm(user_input)

    except Exception as e:
        return f"(⚠️ Error generating response: {str(e)})"

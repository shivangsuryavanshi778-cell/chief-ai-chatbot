"""
chat_console.py
A simple local test interface for your chatbot — runs inside Python only.
"""

from nlu import parse_message
from responder import generate_response
from logger import log_interaction

print("\n🤖 Chatbot ready! Type your message (or 'exit' to quit)\n")

while True:
    user_message = input("You: ")

    if user_message.lower() in ["exit", "quit", "bye"]:
        print("Bot: Bye, Chief 👋 — see you next time!")
        break

    # NLU stage
    nlu_result = parse_message(user_message)

    # Generate bot reply
    bot_reply = generate_response(user_message, nlu_result)

    # Print reply
    print(f"Bot: {bot_reply}")

    # Log conversation (optional)
    log_interaction("local_user", user_message, nlu_result, bot_reply)

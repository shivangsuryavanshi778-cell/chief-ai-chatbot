import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables (for local debugging)
load_dotenv()

# Read API key from Streamlit Secrets (or .env)
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

# Streamlit UI
st.title("🤖 Chief AI Chatbot")
st.write("Hey Chief 👑! I’m your personal AI assistant — powered by OpenRouter.")

user_input = st.text_input("Type your message here:")

if st.button("Send"):
	if not user_input.strip():
		st.warning("Please type something first!")
	else:
		st.chat_message("user").write(user_input)

		headers = {
			"Authorization": f"Bearer {OPENROUTER_API_KEY}",
			"Content-Type": "application/json"
		}

		body = {
			"model": "gpt-3.5-turbo",  # You can replace this with any available model on OpenRouter
			"messages": [{"role": "user", "content": user_input}]
		}

		response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

		if response.status_code == 200:
			reply = response.json()["choices"][0]["message"]["content"]
			st.chat_message("assistant").write(reply)
		else:
			st.error(f"⚠️ Error: {response.status_code} - {response.text}")

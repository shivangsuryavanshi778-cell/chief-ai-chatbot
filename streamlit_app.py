import streamlit as st
import requests
import os
import uuid
from datetime import datetime

# ✅ Import the logger module (for chat history)
import logger

# ==========================================
# STEP 1: Initialize database & create session
# ==========================================
logger.init_db()

# Each browser tab gets a unique session ID (so history is stored separately)
if "session_id" not in st.session_state:
	st.session_state.session_id = str(uuid.uuid4())

SESSION_ID = st.session_state.session_id

# ==========================================
# STEP 2: Load API key safely from Streamlit Secrets or .env
# ==========================================
api_key = None

try:
	if "general" in st.secrets and "OPENROUTER_API_KEY" in st.secrets["general"]:
		api_key = st.secrets["general"]["OPENROUTER_API_KEY"]
	elif "OPENROUTER_API_KEY" in st.secrets:
		api_key = st.secrets["OPENROUTER_API_KEY"]
	else:
		api_key = os.getenv("OPENROUTER_API_KEY")
except Exception as e:
	st.error(f"⚠️ Could not load API key: {e}")

# Debug check (safe): just confirm if key exists, don't print it
if api_key:
	st.success("✅ API key loaded successfully from secrets.")
else:
	st.error("❌ API key not found! Check your Streamlit Secrets formatting.")

# ==========================================
# STEP 3: Chat UI
# ==========================================
st.title("⚡ Zeus Chatbot (created by Shivang)")
st.write("Hey user 👑! Your AI chatbot is live, remembers what you say, and is ready to talk.")

# ✅ Display past conversation (from database)
st.subheader("📜 Conversatio9*n History (this session)")
history = logger.get_history(SESSION_ID)
if history:
	for _id, role, message, created_at in history:
		if role == "user":
			st.chat_message("user").write(message)
		elif role == "assistant":
			st.chat_message("assistant").write(message)
else:
	st.info("No conversation yet. Start chatting below!")

# ==========================================
# STEP 4: Handle new message
# ==========================================
user_input = st.text_input("Type your message here:")

if st.button("Send"):
	if not user_input.strip():
		st.warning("Please type something first!")
	elif not api_key:
		st.error("API key missing! Please check Streamlit Secrets again.")
	else:
		# ✅ Log user message
		logger.log_message(SESSION_ID, "user", user_input)
		st.chat_message("user").write(user_input)

		# Original logic (unchanged)
		headers = {
			"Authorization": f"Bearer {api_key}",
			"HTTP-Referer": "https://chief-ai-chatbot.streamlit.app",
			"X-Title": "ChiefAIChatbot",
			"Content-Type": "application/json"
		}

		body = {
			"model": "gpt-3.5-turbo",
			"messages": [{"role": "user", "content": user_input}]
		}

		response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

		if response.status_code == 200:
			reply = response.json()["choices"][0]["message"]["content"]

			# ✅ Log assistant message
			logger.log_message(SESSION_ID, "assistant", reply)
			st.chat_message("assistant").write(reply)
		else:
			st.error(f"⚠️ Error: {response.status_code} - {response.text}")

# ==========================================
# STEP 5: Optional - Controls to clear/export history
# ==========================================
st.markdown("---")
st.subheader("⚙️ History Controls")
if st.button("🧹 Clear Conversation History"):
	logger.clear_history(SESSION_ID)
	st.success("Conversation history cleared for this session. Reload to see it reset.")

if st.button("📁 Export History to CSV"):
	output_file = f"history_{SESSION_ID}.csv"
	logger.export_history_csv(SESSION_ID, output_file)
	st.success(f"Exported chat history to {output_file}. You can find it in your project folder.")

	# ==========================================
	# STEP 6: LONG-TERM MEMORY CONTROLS
	# ==========================================
	st.markdown("---")
	st.subheader("🧠 Long-Term Memory Controls")

	if st.button("💾 Save This Chat to Memory"):
		if logger.save_memory(SESSION_ID):
			st.success("✅ Conversation saved to long-term memory.")
		else:
			st.warning("⚠️ Nothing to save yet.")

	if st.button("📂 Load Saved Memory"):
		if logger.load_memory(SESSION_ID):
			st.success("✅ Loaded your saved memory successfully.")
			st.rerun()  # refresh page to show loaded chat
		else:
			st.warning("⚠️ No saved memory found for this user.")


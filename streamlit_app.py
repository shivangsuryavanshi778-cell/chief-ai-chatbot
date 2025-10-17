import streamlit as st
import requests
import os
import uuid
from datetime import datetime
import logger  # import local logger module

# ==========================================
# STEP 1: Initialize database & session
# ==========================================
logger.init_db()

if "session_id" not in st.session_state:
	st.session_state.session_id = str(uuid.uuid4())
SESSION_ID = st.session_state.session_id

# ==========================================
# STEP 2: Load API key safely
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

if api_key:
	st.success("✅ API key loaded successfully from secrets.")
else:
	st.error("❌ API key not found! Check your Streamlit Secrets formatting.")

# ==========================================
# STEP 3: Chat UI
# ==========================================
st.set_page_config(page_title="⚡ Zeus AI Chatbot", page_icon="🤖")
st.title("⚡ Zeus AI Chatbot (Now With Memory 🧠)")
st.write("Greetings, mortal! ⚡ I am Zeus AI — your all-knowing digital oracle. Ask me anything!")

# Display past conversation (from DB)
st.subheader("📜 Conversation History (this session)")
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
# STEP 4: Handle user input
# ==========================================
user_input = st.text_input("Type your message here:")

if st.button("Send"):
	if not user_input.strip():
		st.warning("Please type something first!")
	elif not api_key:
		st.error("API key missing! Please check Streamlit Secrets again.")
	else:
		logger.log_message(SESSION_ID, "user", user_input)
		st.chat_message("user").write(user_input)

		headers = {
			"Authorization": f"Bearer {api_key}",
			"HTTP-Referer": "https://chief-ai-chatbot.streamlit.app",
			"X-Title": "ZeusAIChatbot",
			"Content-Type": "application/json"
		}

		body = {
			"model": "gpt-3.5-turbo",
			"messages": [{"role": "user", "content": user_input}]
		}

		response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

		if response.status_code == 200:
			reply = response.json()["choices"][0]["message"]["content"]
			logger.log_message(SESSION_ID, "assistant", reply)
			st.chat_message("assistant").write(reply)
		else:
			st.error(f"⚠️ Error: {response.status_code} - {response.text}")

# ==========================================
# STEP 5: History Controls
# ==========================================
st.markdown("---")
st.subheader("⚙️ History Controls")

col1, col2 = st.columns(2)
with col1:
	if st.button("🧹 Clear Conversation History"):
		logger.clear_history(SESSION_ID)
		st.success("Conversation history cleared for this session. Reload to see it reset.")

with col2:
	if st.button("📁 Export History to CSV"):
		output_file = f"history_{SESSION_ID}.csv"
		logger.export_history_csv(SESSION_ID, output_file)
		st.success(f"Exported chat history to {output_file}.")

# ==========================================
# STEP 6: Long-Term Memory Controls
# ==========================================
st.markdown("---")
st.subheader("🧠 Long-Term Memory Controls")

colA, colB = st.columns(2)

with colA:
	if st.button("💾 Save This Chat to Memory"):
		success, msg = logger.save_memory(SESSION_ID)
		if success:
			st.success("✅ " + msg)
		else:
			st.warning("⚠️ " + msg)

with colB:
	if st.button("📂 Load Saved Memory"):
		success, msg = logger.load_memory(SESSION_ID)
		if success:
			st.success("✅ " + msg)
			# 🔄 Streamlit rerun compatibility for all versions
			if hasattr(st, "rerun"):
				st.rerun()
			elif hasattr(st, "experimental_rerun"):
				st.experimental_rerun()
			else:
				st.warning("⚠️ Unable to rerun Streamlit — please refresh manually.")

		else:
			st.warning("⚠️ " + msg)

import streamlit as st
import requests
import os
import uuid
from datetime import datetime
import logger
import memory_manager

# ==========================================
# STEP 1: Initialize database & session
# ==========================================
logger.init_db()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
SESSION_ID = st.session_state.session_id

# Load persistent memory automatically
USER_MEMORY = memory_manager.load_user_memory(SESSION_ID)

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
st.title("⚡ Zeus AI Chatbot (Now With Automatic Memory 🧠)")
st.write("Greetings, mortal! ⚡ I am Zeus AI — your all-knowing digital oracle. I remember your past conversations automatically.")

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

        # Combine previous chat context with user memory for better contextual responses
        combined_context = f"User memory: {USER_MEMORY}\nUser said: {user_input}"

        body = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": combined_context}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            logger.log_message(SESSION_ID, "assistant", reply)
            st.chat_message("assistant").write(reply)

            # 🧠 Update memory automatically
            USER_MEMORY["last_message"] = user_input
            USER_MEMORY["last_reply"] = reply
            USER_MEMORY["conversation_count"] = USER_MEMORY.get("conversation_count", 0) + 1
            USER_MEMORY["last_interaction"] = datetime.utcnow().isoformat()
            memory_manager.save_user_memory(SESSION_ID, USER_MEMORY)
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
# STEP 6: Persistent Memory Controls
# ==========================================
st.markdown("---")
st.subheader("💾 Zeus Memory (Automatic & Persistent)")

colA, colB = st.columns(2)

with colA:
    if st.button("🧠 View My Memory"):
        mem = memory_manager.load_user_memory(SESSION_ID)
        if mem:
            st.json(mem)
        else:
            st.info("No memory stored yet. Chat to let Zeus remember you!")

with colB:
    if st.button("🧹 Clear My Memory"):
        memory_manager.clear_user_memory(SESSION_ID)
        st.success("✅ Zeus has forgotten your past memories.")

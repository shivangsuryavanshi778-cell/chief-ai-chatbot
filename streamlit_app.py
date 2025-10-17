import streamlit as st
import requests
import os
from datetime import datetime
import logger
import memory_manager

# ==========================================
# STEP 1: LOGIN PAGE (User Identification)
# ==========================================
st.set_page_config(page_title="⚡ Zeus AI Chatbot", page_icon="🤖")

if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.title("⚡ Zeus AI Chatbot — Login")
    st.subheader("Welcome, mortal! ⚡ Enter your name to begin.")
    username_input = st.text_input("Enter your name:")

    if st.button("Start Chat"):
        if not username_input.strip():
            st.warning("Please enter your name to continue.")
        else:
            st.session_state.username = username_input.strip()

            # 🔄 Safe rerun for all Streamlit versions
            if hasattr(st, "rerun"):
                st.rerun()
            elif hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.info("✅ Logged in! Please manually refresh if the chat doesn't load automatically.")

else:
    # ==========================================
    # Continue rest of your chatbot code below
    # ==========================================
    # (everything that was grey before remains under this 'else')


# ==========================================
# STEP 2: Initialize DB & Load User Memory
# ==========================================
USERNAME = st.session_state.username
st.sidebar.success(f"🧠 Logged in as: {USERNAME}")

logger.init_db()
USER_MEMORY = memory_manager.load_user_memory(USERNAME)

# ==========================================
# STEP 3: Load API Key
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
# STEP 4: Main Chat Interface
# ==========================================
st.title(f"⚡ Zeus AI Chatbot (Welcome back, {USERNAME}!)")
st.write("I remember our past conversations — let's continue where we left off.")

st.subheader("📜 Conversation History")
history = logger.get_history(USERNAME)
if history:
    for _id, role, message, created_at in history:
        if role == "user":
            st.chat_message("user").write(message)
        elif role == "assistant":
            st.chat_message("assistant").write(message)
else:
    st.info("No conversation yet. Start chatting below!")

# ==========================================
# STEP 5: User Input
# ==========================================
user_input = st.text_input("Type your message here:")

if st.button("Send"):
    if not user_input.strip():
        st.warning("Please type something first!")
    elif not api_key:
        st.error("API key missing! Please check Streamlit Secrets again.")
    else:
        logger.log_message(USERNAME, "user", user_input)
        st.chat_message("user").write(user_input)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://chief-ai-chatbot.streamlit.app",
            "X-Title": "ZeusAIChatbot",
            "Content-Type": "application/json",
        }

        combined_context = f"User memory: {USER_MEMORY}\nUser said: {user_input}"

        body = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": combined_context}],
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body,
        )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            logger.log_message(USERNAME, "assistant", reply)
            st.chat_message("assistant").write(reply)

            # 🧠 Update memory automatically
            USER_MEMORY["last_message"] = user_input
            USER_MEMORY["last_reply"] = reply
            USER_MEMORY["conversation_count"] = (
                    USER_MEMORY.get("conversation_count", 0) + 1
            )
            USER_MEMORY["last_interaction"] = datetime.utcnow().isoformat()
            memory_manager.save_user_memory(USERNAME, USER_MEMORY)
        else:
            st.error(f"⚠️ Error: {response.status_code} - {response.text}")

# ==========================================
# STEP 6: Memory & History Controls
# ==========================================
st.markdown("---")
st.subheader("⚙️ Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧹 Clear Chat History"):
        logger.clear_history(USERNAME)
        st.success("Conversation history cleared. Refresh to see it reset.")

with col2:
    if st.button("💾 View My Memory"):
        mem = memory_manager.load_user_memory(USERNAME)
        if mem:
            st.json(mem)
        else:
            st.info("No memory stored yet. Chat more to let Zeus remember you!")

with col3:
    if st.button("🚪 Logout"):
        st.session_state.username = None
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.info("Logged out — please refresh manually.")

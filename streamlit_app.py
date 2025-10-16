import streamlit as st
import requests
import os

# ==========================================
# STEP 1: Load API key safely from Streamlit Secrets or .env
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
# STEP 2: Build Chat UI
# ==========================================
st.title("🤖 Chief AI Chatbot")
st.write("Hey Chief 👑! Your AI chatbot is live and ready to talk.")

user_input = st.text_input("Type your message here:")

if st.button("Send"):
    if not user_input.strip():
        st.warning("Please type something first!")
    elif not api_key:
        st.error("API key missing! Please check Streamlit Secrets again.")
    else:
        st.chat_message("user").write(user_input)

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
            st.chat_message("assistant").write(reply)
        else:
            st.error(f"⚠️ Error: {response.status_code} - {response.text}")

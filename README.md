# 🤖 Chief AI Chatbot

### _Your personal AI assistant built using Python, Streamlit, and OpenRouter_

Chief AI Chatbot is an intelligent conversational assistant designed to provide precise, contextual, and dynamic responses — all running through the OpenRouter API and hosted seamlessly on Streamlit Cloud.

---

## 🚀 Features

✅ Built with **Streamlit** for an interactive, modern chat UI  
✅ Powered by **OpenRouter API** (no OpenAI billing required)  
✅ Modular design — easy to customize or expand  
✅ Secure API key management via **Streamlit Secrets**  
✅ Can be **embedded** in your portfolio or website via iframe  
✅ Fully deployable on **Streamlit Cloud**  

---

## 🧩 Project Structure

chief-ai-chatbot/
│
├── streamlit_app.py # Main chatbot frontend
├── responder.py # (Optional) response logic and NLU module
├── requirements.txt # Dependencies
├── .gitignore # Ignores .env and cache files
├── .env.example # Example environment file
└── README.md # Documentation

---

## ⚙️ Installation (Local Setup)

Follow these steps to run the chatbot locally inside **PyCharm** or any IDE.

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/shivangsuryavanshi778-cell/chief-ai-chatbot.git
cd chief-ai-chatbot

2️⃣ Create a Virtual Environment (Optional but Recommended)
python -m venv venv
venv\Scripts\activate  # (Windows)
source venv/bin/activate  # (Mac/Linux)

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Create Your .env File

Create a file named .env in the root folder and add your API key:

OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
LLM_PROVIDER=openrouter

5️⃣ Run the Chatbot Locally
streamlit run streamlit_app.py


Now open the local URL (e.g., http://localhost:8501) to chat with your AI!

🌐 Streamlit Cloud Deployment
1️⃣ Push Code to GitHub

Make sure your latest version (with streamlit_app.py) is pushed to GitHub.

git add .
git commit -m "Initial commit"
git push origin main

2️⃣ Deploy on Streamlit Cloud

Go to https://share.streamlit.io

Log in using your GitHub account

Click “New app”

Choose your repo → branch main → main file: streamlit_app.py

Click Deploy

🔐 Add Secrets (for API key)

On Streamlit Cloud:

Click Manage app → Secrets

Paste this (TOML format):

[general]
OPENROUTER_API_KEY = "sk-or-v1-your-real-key-here"
LLM_PROVIDER = "openrouter"


Save and Reboot app.

🧠 How It Works

streamlit_app.py loads your API key securely from Streamlit Secrets.

When the user types a message, it sends a POST request to the OpenRouter endpoint:
https://openrouter.ai/api/v1/chat/completions

The response is displayed using Streamlit’s st.chat_message() components.

No external backend or database required — runs entirely via API calls.

📦 Requirements
Library	Purpose
streamlit	Web interface
requests	API communication
python-dotenv	Local .env file handling
os	Environment access

🧰 Optional Enhancements

Add contextual memory (conversation history)

Integrate embeddings or document search

Connect to Instagram / Telegram API

Deploy on a custom domain

Add analytics & message logging

🛡️ Security Notes

⚠️ Never upload your .env file or real API key to GitHub.
Always use .gitignore to exclude it:

.env
__pycache__/
.venv/

💬 Example Chat
User: Hey Chief AI 👑, how are you?
Bot: I’m doing great, Chief! Ready to help you with anything you need today.

**👑 Author
Shivang Suryavanshi
BBA Student | AI & Marketing Enthusiast
**

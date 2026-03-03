import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import requests

load_dotenv()

# API KEYS
GROQ_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_response(prompt):
    # 2️⃣ Try Groq
    try:
        if GROQ_KEY:
            client = Groq(api_key=GROQ_KEY)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
    except Exception as e:
        print("Groq failed:", e)

    # 3️⃣ Try OpenRouter
    try:
        if OPENROUTER_KEY:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("OpenRouter failed:", e)

    return "⚠ All AI providers are currently unavailable."

def run():
    
    # 🔥 HERO BANNER
    st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 40px;
        border-radius: 25px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #cbd5e1;
    }
    </style>

    <div class="hero-banner">
        <div class="hero-title">💬 AI Chatbot</div>
        <div class="hero-subtitle">
            Ask anything and get intelligent responses powered by Gemini.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your message..."):

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
                st.markdown(prompt)

        reply = generate_response(prompt)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

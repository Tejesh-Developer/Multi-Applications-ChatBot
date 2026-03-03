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
                model="llama3-70b-8192",
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

    st.markdown("""
        <style>
        .output-box {
            background-color: #161B22;
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

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
        <div class="hero-title">📝 AI Text Generation</div>
            <div class="hero-subtitle">
                Generate high-quality content instantly using Gemini.
            </div>
        </div>
    """, unsafe_allow_html=True)

    prompt = st.text_area("Enter your prompt:", height=120)

    col1, col2 = st.columns([1,1])

    with col1:
        generate = st.button("🚀 Generate")

    with col2:
        clear = st.button("🗑 Clear")

    if clear:
        st.session_state.generated_text = ""

    if generate and prompt:
        with st.spinner("Generating content..."):
            st.session_state.generated_text = generate_response(prompt)

    if "generated_text" in st.session_state and st.session_state.generated_text:
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.generated_text)
        st.markdown('</div>', unsafe_allow_html=True)
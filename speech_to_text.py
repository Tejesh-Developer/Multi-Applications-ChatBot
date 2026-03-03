import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
# 🔐 API KEYS
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

from groq import Groq



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
        <div class="hero-title">🎤 Speech to Text</div>
            <div class="hero-subtitle">
                Upload an audio file and convert speech into text using Gemini.
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "flac"])

    if uploaded_file:
        audio_data = uploaded_file.read()

        if st.button("🚀 Transcribe"):
            with st.spinner("Transcribing..."):
                
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))

                transcription = client.audio.transcriptions.create(
                    file=uploaded_file,
                    model="whisper-large-v3"
                )

                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.markdown("### 📝 Transcription Result")
                st.write(transcription.text)
                st.markdown('</div>', unsafe_allow_html=True)
            
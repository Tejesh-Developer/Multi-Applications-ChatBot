import streamlit as st
from gtts import gTTS
import os

def run():

    st.markdown("""
        <style>
        .tts-box {
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
        <div class="hero-title">🎙 Text to Speech</div>
            <div class="hero-subtitle">
                Convert your text into natural AI speech using Gemini.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    text_input = st.text_area("Enter text to convert:", height=150)

    if st.button("🚀 Generate Speech") and text_input:

        with st.spinner("Generating audio..."):

            tts = gTTS(text=text_input, lang="en")
            file_name = "generated_audio.mp3"
            tts.save(file_name)

            st.markdown('<div class="tts-box">', unsafe_allow_html=True)
            st.markdown("### 🔊 Generated Audio")
            st.audio(file_name)
            st.download_button(
                "⬇ Download Audio",
                data=open(file_name, "rb"),
                file_name="ai_speech.mp3"
            )
            st.markdown('</div>', unsafe_allow_html=True)
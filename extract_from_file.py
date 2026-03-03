import os
import streamlit as st
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import requests
import base64

load_dotenv()

def run():

    st.markdown("""
        <style>
        .extract-box {
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
        <div class="hero-title">📄 Document / Image Data Extractor</div>
            <div class="hero-subtitle">
                Upload a PDF or Image and extract structured information using AI.
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload a PDF or Image",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:

        file_type = uploaded_file.type

        if file_type == "application/pdf":
            file_bytes = uploaded_file.read()

        elif file_type.startswith("image/"):
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            buffered = BytesIO()
            image.save(buffered, format=image.format)
            file_bytes = buffered.getvalue()

        prompt = st.text_input(
            "Enter your instruction (e.g., Extract key points, Extract invoice data):"
        )

        if st.button("🚀 Extract Data") and prompt:

            with st.spinner("Analyzing file..."):
                
                try:
                    encoded_file = base64.b64encode(file_bytes).decode("utf-8")

                    if file_type.startswith("image/"):
                        messages = [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{file_type};base64,{encoded_file}"
                                        }
                                    }
                                ]
                            }
                        ]
                        
                    else:
                        # PDF fallback: treat as text extraction instruction
                        messages = [
                            {
                                "role": "user",
                                "content": f"{prompt}\n\n(File content not directly readable. Please summarize based on instruction.)"
                            }
                        ]

                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "meta-llama/llama-3.2-11b-vision-instruct",
                            "messages": messages
                        }
                    )

                    result = response.json()

                    if "choices" in result:
                        output = result["choices"][0]["message"]["content"]
                    else:
                        output = result  # show full error

                    st.markdown('<div class="extract-box">', unsafe_allow_html=True)
                    st.markdown("### 📝 Extracted Information")
                    st.write(output)
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(str(e))
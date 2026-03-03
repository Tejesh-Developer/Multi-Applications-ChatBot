import os
import streamlit as st
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import requests

load_dotenv()


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
        <div class="hero-title">🖼 Image Summarization</div>
            <div class="hero-subtitle">
                Upload an image and generate AI-powered description or analysis.
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        # Safely get image bytes
        img_bytes = uploaded_file.getvalue()

        # Display image
        image = Image.open(BytesIO(img_bytes))
        st.image(image, caption="Uploaded Image", use_container_width=True)

        # Select summary type
        prompt_type = st.selectbox(
            "Choose what you want:",
            [
                "Describe this image in detail",
                "Generate a short caption",
                "Explain what is happening in this image",
                "List objects visible in the image"
            ]
        )

        if st.button("🚀 Generate Summary"):

            with st.spinner("Analyzing image..."):

                try:
                    import base64

                    image_base64 = base64.b64encode(img_bytes).decode("utf-8")

                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "meta-llama/llama-3.2-11b-vision-instruct",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_type},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:{uploaded_file.type};base64,{image_base64}"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    )

                    result = response.json()

                    st.markdown("### 📝 AI Generated Output")
                    st.write(result["choices"][0]["message"]["content"])

                except Exception as e:
                    st.error("Error processing image.")
                    st.error(str(e))
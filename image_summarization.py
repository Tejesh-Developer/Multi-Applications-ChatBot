import os
import base64
import streamlit as st
from PIL import Image, ImageStat
from io import BytesIO
from dotenv import load_dotenv
import requests

load_dotenv()

# ── AI Call ───────────────────────────────────────────────────────────────────

def analyze_image(img_bytes, mime_type, prompt):
    """Send image to LLaMA Vision via OpenRouter."""
    image_base64 = base64.b64encode(img_bytes).decode("utf-8")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-oss-120b",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }
    )
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"API Error: {result}"


def get_image_info(img_bytes, uploaded_file):
    """Get basic image metadata."""
    image = Image.open(BytesIO(img_bytes))
    width, height = image.size
    mode   = image.mode
    fmt    = image.format or uploaded_file.type.split("/")[-1].upper()
    size_kb = round(len(img_bytes) / 1024, 1)
    return image, width, height, mode, fmt, size_kb


# ── Analysis Presets ──────────────────────────────────────────────────────────

ANALYSIS_MODES = {
    "🔍 Detailed Description": {
        "prompt": "Describe this image in full detail. Include: main subject, background, colors, lighting, mood, and any text visible. Be thorough and structured.",
        "desc":   "Full detailed analysis of everything in the image"
    },
    "📝 Short Caption": {
        "prompt": "Write a single short, punchy caption for this image. Max 15 words. Make it engaging and descriptive.",
        "desc":   "One-line caption perfect for social media or presentations"
    },
    "📦 List All Objects": {
        "prompt": "List every object, person, animal, and element visible in this image. Format as a clean numbered list. Group by category if possible.",
        "desc":   "Complete inventory of everything visible in the image"
    },
    "🎭 Scene & Story": {
        "prompt": "What is happening in this image? Tell the story behind it. Who is involved, what are they doing, what led to this moment, and what might happen next?",
        "desc":   "Narrative interpretation of the scene"
    },
    "🎨 Color & Style Analysis": {
        "prompt": "Analyze the visual style of this image. Describe: dominant colors with hex codes if possible, color palette mood, photography/art style, lighting conditions, composition technique, and overall aesthetic.",
        "desc":   "Color palette, style, lighting and composition breakdown"
    },
    "🏷 Tags & Keywords": {
        "prompt": "Generate 20 relevant tags/keywords for this image. Include: subjects, actions, colors, mood, style, setting. Format as comma-separated tags. Also suggest 3 potential use cases for this image.",
        "desc":   "SEO tags, keywords and use case suggestions"
    },
    "🧠 Smart Q&A": {
        "prompt": None,  # Custom — user types their own question
        "desc":   "Ask any custom question about this image"
    },
}


# ── Main Run ──────────────────────────────────────────────────────────────────

def run():

    # Usage tracking
    try:
        import database
        database.log_usage(st.session_state.get("username", "unknown"), "Image Summarization")
    except:
        pass

    # ── Styles ────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 40px; border-radius: 25px; margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .hero-title    { font-size: 42px; font-weight: 800; color: white; margin-bottom: 10px; }
    .hero-subtitle { font-size: 18px; color: #cbd5e1; }

    .img-meta-card {
        background: #111827; border: 1px solid #1f2937;
        border-radius: 14px; padding: 16px 20px; margin-bottom: 20px;
    }
    .meta-pill {
        display: inline-block; background: #1f2937; color: #38bdf8;
        padding: 3px 12px; border-radius: 16px; font-size: 12px;
        margin: 3px; border: 1px solid #374151;
    }
    .result-box {
        background: #111827; border: 1px solid #1f2937;
        border-radius: 14px; padding: 22px 24px; margin-top: 16px;
    }
    .result-title {
        font-size: 15px; font-weight: 700; color: #38bdf8;
        margin-bottom: 14px; padding-bottom: 8px;
        border-bottom: 1px solid #1f2937;
    }
    .mode-desc {
        font-size: 12px; color: #64748b; margin-top: 4px;
    }
    .history-item {
        background: #0f1923; border: 1px solid #1f2937;
        border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🖼 Image Summarization</div>
        <div class="hero-subtitle">
            Upload an image — get AI-powered descriptions, captions, tags, style analysis and more.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Session state ─────────────────────────────────────────────────────────
    if "img_history" not in st.session_state:
        st.session_state.img_history = []

    # ── Layout: Left = upload+controls, Right = image preview ─────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        uploaded_file = st.file_uploader(
            "📂 Upload Image",
            type=["png", "jpg", "jpeg", "webp"],
            help="Supports PNG, JPG, JPEG, WebP"
        )

        if uploaded_file:
            img_bytes = uploaded_file.getvalue()
            image, w, h, mode, fmt, size_kb = get_image_info(img_bytes, uploaded_file)

            # Image metadata pills
            st.markdown(f"""
            <div class="img-meta-card">
                <b style="color:#e2e8f0;">📄 {uploaded_file.name}</b><br><br>
                <span class="meta-pill">📐 {w} × {h} px</span>
                <span class="meta-pill">🎨 {mode}</span>
                <span class="meta-pill">📦 {fmt}</span>
                <span class="meta-pill">💾 {size_kb} KB</span>
            </div>
            """, unsafe_allow_html=True)

            # Analysis mode selector
            selected_mode = st.selectbox(
                "🎯 Analysis Mode",
                list(ANALYSIS_MODES.keys()),
                help="Choose what kind of analysis you want"
            )

            mode_info = ANALYSIS_MODES[selected_mode]
            st.markdown(f'<div class="mode-desc">ℹ {mode_info["desc"]}</div>',
                        unsafe_allow_html=True)

            # Custom question for Smart Q&A
            custom_question = ""
            if selected_mode == "🧠 Smart Q&A":
                custom_question = st.text_input(
                    "💬 Your Question",
                    placeholder="e.g. What brand is visible? What text can you read? Is this indoors or outdoors?",
                    key="custom_q"
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Analyze button
            btn_disabled = (selected_mode == "🧠 Smart Q&A" and not custom_question)
            analyze_btn  = st.button(
                "🚀 Analyze Image",
                use_container_width=True,
                disabled=btn_disabled
            )

            # Clear history
            if st.session_state.img_history:
                if st.button("🗑 Clear History", use_container_width=True):
                    st.session_state.img_history = []
                    st.rerun()

    with col_right:
        if uploaded_file:
            st.image(image, caption=f"📸 {uploaded_file.name}", use_container_width=True)

            # Thumbnail download
            thumb = image.copy()
            thumb.thumbnail((400, 400))
            buf_thumb = BytesIO()
            thumb.save(buf_thumb, format="PNG")
            buf_thumb.seek(0)
            st.download_button(
                "⬇ Download Thumbnail (400×400)",
                data=buf_thumb,
                file_name=f"thumb_{uploaded_file.name}",
                mime="image/png",
                use_container_width=True
            )

    # ── Run Analysis ──────────────────────────────────────────────────────────
    if uploaded_file and analyze_btn:
        prompt = (custom_question
                  if selected_mode == "🧠 Smart Q&A"
                  else mode_info["prompt"])

        with st.spinner(f"🤖 Analyzing image with AI..."):
            try:
                result_text = analyze_image(img_bytes, uploaded_file.type, prompt)

                # Save to history
                st.session_state.img_history.insert(0, {
                    "mode":   selected_mode,
                    "prompt": prompt,
                    "result": result_text,
                    "name":   uploaded_file.name,
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")
                result_text = None

    # ── Results Display ───────────────────────────────────────────────────────
    if st.session_state.img_history:
        latest = st.session_state.img_history[0]

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="result-title">{latest["mode"]} — {latest["name"]}</div>',
                    unsafe_allow_html=True)
        st.markdown(latest["result"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Download result
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                "⬇ Download as .txt",
                data=latest["result"],
                file_name=f"{uploaded_file.name.rsplit('.',1)[0]}_analysis.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_d2:
            md_content = f"# Image Analysis: {latest['name']}\n\n**Mode:** {latest['mode']}\n\n---\n\n{latest['result']}"
            st.download_button(
                "⬇ Download as .md",
                data=md_content,
                file_name=f"{uploaded_file.name.rsplit('.',1)[0]}_analysis.md",
                mime="text/markdown",
                use_container_width=True
            )

        # ── History (previous analyses) ───────────────────────────────────────
        if len(st.session_state.img_history) > 1:
            st.markdown("---")
            st.markdown("#### 🕒 Previous Analyses")
            for i, item in enumerate(st.session_state.img_history[1:], 1):
                with st.expander(f"{item['mode']} — {item['name']}"):
                    st.markdown(item["result"])

    elif not uploaded_file:
        # Empty state
        st.markdown("""
        <div style="background:#111827;border:1px dashed #374151;
             border-radius:16px;padding:40px;text-align:center;margin-top:20px;">
            <div style="font-size:48px;margin-bottom:16px;">🖼</div>
            <div style="font-size:20px;font-weight:700;color:#e2e8f0;margin-bottom:12px;">
                Upload an image to get started
            </div>
            <div style="font-size:13px;color:#64748b;">
                Supports PNG · JPG · JPEG · WebP<br><br>
                🔍 Detailed Description &nbsp;·&nbsp;
                📝 Captions &nbsp;·&nbsp;
                📦 Object List &nbsp;·&nbsp;
                🎨 Style Analysis &nbsp;·&nbsp;
                🏷 Tags &nbsp;·&nbsp;
                🧠 Custom Q&A
            </div>
        </div>
        """, unsafe_allow_html=True)
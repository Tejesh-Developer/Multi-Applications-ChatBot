import streamlit as st
from streamlit_option_menu import option_menu
import auth
import plotly.express as px
import pandas as pd
import streamlit as st
from auth import login

# Check authentication
st.set_page_config(layout="wide")
if not auth.login():
    st.stop()
# ======= MAIN APP STARTS HERE =======
st.sidebar.success(f"Welcome {st.session_state.username}")

# Mee AI features ikkada start avvali

st.set_page_config(layout="wide", page_title="GenAI Applications")

# 🔐 LOGIN CHECK FIRST
if not auth.login():
    st.stop()

# 👤 TOP RIGHT USER PROFILE

if "username" in st.session_state:

    col1, col2 = st.columns([8,2])

    with col2:
        with st.popover(f"👤 {st.session_state.username}"):
            st.markdown("### 👤 Profile")
            st.write(f"Username: **{st.session_state.username}**")
            # st.divider()
            if st.button("🚪 Logout"):
                auth.logout()

# 🧭 Sidebar After Login
with st.sidebar:
    selected = option_menu(
        "🤖 GenAI Modules",
        [
            "Home",
            "Chatbot",
            "Text Generation",
            "Speech to Text",
            "Text to Speech",
            "Image Summarization",
            "Extract From File",
            "PPT Slide Preparation"
        ],
        icons=[
            "house",
            "chat-dots",
            "file-text",
            "mic",
            "volume-up",
            "image",
            "file-earmark",
            "bar-chart"
        ],
        default_index=0,
    )

    if st.button("🚪 Logout"):
        auth.logout()

# ---------- Routing ----------
if selected == "Home":
    st.title("🤖 GenAI Applications")
    st.subheader("Multi-Feature Generative AI Suite")

elif selected == "Chatbot":
    import chatbot
    chatbot.run()

elif selected == "Text Generation":
    import text_generation
    text_generation.run()

elif selected == "Speech to Text":
    import speech_to_text
    speech_to_text.run()

elif selected == "Text to Speech":
    import text_to_speech
    text_to_speech.run()

elif selected == "Image Summarization":
    import image_summarization
    image_summarization.run()

elif selected == "Extract From File":
    import extract_from_file
    extract_from_file.run()

elif selected == "PPT Slide Preparation":
    import ppt_slide_preparation
    ppt_slide_preparation.run()

if selected == "Home":

    username = "Tejesh"

    st.markdown("""
    <style>
    .hero {
        padding: 35px;
        border-radius: 20px;
        # background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        background: linear-gradient(90deg, #1f4037, #99f2c8);
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        margin-bottom: 30px;
    }

    .stat-card {
        background: #111827;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }

    .recent-box {
        background: #1f2937;
        padding: 20px;
        border-radius: 12px;
    }

    .footer {
        text-align: center;
        margin-top: 40px;
        opacity: 0.6;
    }
    </style>
    """, unsafe_allow_html=True)

    # 🚀 HERO
    st.markdown(f"""
    <div class="hero">
        <h1>🚀 Welcome back, {username}</h1>
        <p>Manage and explore powerful AI tools from one dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
    

    # 📊 Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="stat-card"><h3>8+</h3><p>AI Modules</p></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="stat-card"><h3>120+</h3><p>Total Uses</p></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="stat-card"><h3>⚡ Fast</h3><p>Real-Time AI</p></div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="stat-card"><h3>🔒 Secure</h3><p>Login Protected</p></div>', unsafe_allow_html=True)

    st.markdown("---")


import database

if st.session_state.username == "admin":

    # ===== Admin Header =====
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;">
            <h2 style="color:white;">🛠 Admin Control Panel</h2>
            <p style="color:white;">Manage users and monitor system activity</p>
        </div>
    """, unsafe_allow_html=True)

    # ===== Admin Card =====
    st.markdown("""
        <div style="
            background-color: #111827;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        ">
    """, unsafe_allow_html=True)

    st.subheader("👥 User Management")

    users = database.get_all_users()
    selected_user = st.selectbox("Select User to Delete", users)

    col1, col2 = st.columns([1,3])

    with col1:
        if st.button("❌ Delete User"):
            if selected_user == "admin":
                st.warning("⚠ Admin account cannot be deleted.")
            else:
                database.delete_user(selected_user)
                st.success(f"✅ {selected_user} deleted successfully!")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


    # 📈 Analytics Chart
    data = pd.DataFrame({
        "Module": ["Chatbot", "Text Gen", "Speech", "Image", "PPT"],
        "Usage": [40, 30, 20, 15, 10]
    })

    fig = px.bar(
        data,
        x="Module",
        y="Usage",
        color="Module",
        title="📊 Module Usage Analytics",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 🕒 Recent Activity
    st.markdown("### 🕒 Recent Activity")

    st.markdown("""
    <div class="recent-box">
    ✔ Chatbot used for project explanation<br><br>
    ✔ Generated marketing content<br><br>
    ✔ Converted speech to text<br><br>
    ✔ Created AI presentation slides
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
    🌟 GenAI Suite v3.0 | Ultra Pro Dashboard
    </div>
    """, unsafe_allow_html=True)

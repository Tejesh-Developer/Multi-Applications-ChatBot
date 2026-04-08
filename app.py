import streamlit as st
from streamlit_option_menu import option_menu
import auth
import database

st.set_page_config(
    page_title="GenAI App",
    page_icon="🤖",
    layout="wide"
)

if not auth.login():
    st.stop()

# Theme toggle
st.sidebar.markdown("### 🎨 Appearance")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

if dark_mode:
    st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #111827; }
    .block-container { padding-top: 2rem; }
    .stButton>button { background-color: #1f2937; color: white; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background-color: #f5f7fb; color: #111827; }
    section[data-testid="stSidebar"] { background-color: #ffffff; }
    .stButton>button { background-color: #ffffff; color: #111827; border-radius: 10px; border: 1px solid #d1d5db; }
    </style>
    """, unsafe_allow_html=True)

# Top-right profile
col1, col2 = st.columns([8, 2])
with col2:
    with st.popover(f"👤 {st.session_state.username}"):
        st.markdown("### 👤 Profile")
        st.write(f"Username: **{st.session_state.username}**")
        if st.button("🚪 Logout", key="popover_logout"):
            auth.logout()

# Sidebar nav
with st.sidebar:
    st.sidebar.success(f"Welcome {st.session_state.username}")
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
            "Document Q&A",
            "PPT Slide Preparation",
        ],
        icons=[
            "house", "chat-dots", "file-text", "mic",
            "volume-up", "image", "file-earmark",
            "journal-text", "bar-chart",
        ],
        default_index=0,
    )
    if st.button("🚪 Logout", key="sidebar_logout"):
        auth.logout()

# Routing
if selected == "Home":
    username = st.session_state.username
    st.markdown("""
    <style>
    .hero { padding:35px;border-radius:20px;
        background:linear-gradient(90deg,#1a1a2e,#16213e,#0f3460);
        color:white;box-shadow:0 10px 30px rgba(0,0,0,0.4);margin-bottom:30px; }
    .stat-card { background:#111827;padding:25px;border-radius:15px;
        text-align:center;box-shadow:0 6px 20px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hero">
        <h1>🚀 Welcome back, {username}</h1>
        <p>Manage and explore powerful AI tools from one dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown('<div class="stat-card"><h3>9+</h3><p>AI Modules</p></div>', unsafe_allow_html=True)
    with c2:
        total = database.get_total_usage()
        st.markdown(f'<div class="stat-card"><h3>{total}</h3><p>Total Uses</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="stat-card"><h3>⚡ Fast</h3><p>Real-Time AI</p></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="stat-card"><h3>🔒 Secure</h3><p>Login Protected</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.username == "admin":
        import admin
        admin.run()

elif selected == "Chatbot":
    import chatbot; chatbot.run()

elif selected == "Text Generation":
    import text_generation; text_generation.run()

elif selected == "Speech to Text":
    import speech_to_text; speech_to_text.run()

elif selected == "Text to Speech":
    import text_to_speech; text_to_speech.run()

elif selected == "Image Summarization":
    import image_summarization; image_summarization.run()

elif selected == "Extract From File":
    import extract_from_file; extract_from_file.run()

elif selected == "Document Q&A":
    import document_qa; document_qa.run()

elif selected == "PPT Slide Preparation":
    import ppt_slide_preparation; ppt_slide_preparation.run()
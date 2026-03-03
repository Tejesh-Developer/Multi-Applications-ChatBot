import streamlit as st
from database import create_table, login_user, register_user

def login():
    create_table()

    # Session defaults
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.authenticated:
        return True

    # ====== GLOBAL STYLE ======
    st.markdown("""
    <style>
    .stApp {
        background-color: #0b1120;
    }

    .hero {
        background: linear-gradient(135deg, #1f4037, #99f2c8);
        padding: 35px;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 60px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    }

    .hero h1 {
        font-size: 34px;
        font-weight: 800;
        color: #0f172a;
    }

    .hero p {
        font-size: 16px;
        color: #0f172a;
        margin-top: 8px;
    }

    .login-title {
        font-size: 34px;
        font-weight: 700;
        background: linear-gradient(90deg,#38bdf8,#22c55e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sub-text {
        color: #94a3b8;
        font-size: 15px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ===== HERO SECTION =====
    st.markdown("""
    <div class="hero">
        <h1>🚀 Welcome to GenAI Suite</h1>
        <p>Access powerful AI tools from one unified dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

    # ===== CENTER BIG CARD =====
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:

        st.markdown("""
        <div style='text-align:center;margin-bottom:30px;'>
            <div class='login-title'>🔐 Login to GenAI Suite</div>
            <div class='sub-text'>Secure access to your AI dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        # ================= LOGIN =================
        if not st.session_state.show_signup:

            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            st.markdown("""
            <style>
            .stButton > button {
                height: 55px;
                font-size: 18px;
                font-weight: 700;
                border-radius: 12px;
                background: linear-gradient(90deg, #38bdf8, #22c55e);
                color: white;
                border: none;
                transition: 0.3s ease;
            }

            .stButton > button:hover {
               transform: scale(1.03);
               box-shadow: 0 5px 15px rgba(34,197,94,0.3);
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 LOGIN", use_container_width=True):

                user = login_user(username.strip(), password.strip())

                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error("Invalid username or password")

            st.markdown("<div style='text-align:center;margin-top:20px;color:#94a3b8;'>Don't have an account?</div>", unsafe_allow_html=True)

            if st.button("Register here", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()

        # ================= SIGNUP =================
        else:

            new_user = st.text_input("Username", key="signup_user")
            new_pass = st.text_input("Password", type="password", key="signup_pass")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            st.markdown("""
            <style>
            .stButton > button {
                height: 55px;
                font-size: 18px;
                font-weight: 700;
                border-radius: 12px;
                background: linear-gradient(90deg, #38bdf8, #22c55e);
                color: white;
                border: none;
                transition: 0.3s ease;
            }

            .stButton > button:hover {
               transform: scale(1.03);
               box-shadow: 0 5px 15px rgba(34,197,94,0.3);
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("📝 CREATE ACCOUNT", use_container_width=True):

                if new_pass != confirm:
                    st.error("Passwords do not match")

                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters")

                else:
                    success = register_user(new_user.strip(), new_pass.strip())

                    if success:
                        st.success("Account created successfully! Please login.")

                        st.session_state["login_user"] = ""
                        st.session_state["login_pass"] = ""
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error("Username already exists")

            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()

    return False


def logout():
    st.session_state.clear()   # 🔥 Clear all session data
    st.rerun()


def logout():
    if "authenticated" in st.session_state:
        st.session_state.authenticated = False
    st.rerun()


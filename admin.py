import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import database

# ── Module icons map ──────────────────────────────────────────────────────────
MODULE_ICONS = {
    "Chatbot":             "💬",
    "Text Generation":     "📝",
    "Speech to Text":      "🎤",
    "Text to Speech":      "🔊",
    "Image Summarization": "🖼",
    "Extract from File":   "📄",
    "PPT Preparation":     "📊",
    "Image Generation":    "🎨",
}

STATUS_COLOR = {"success": "🟢", "error": "🔴", "warning": "🟡"}

# ── Styles ────────────────────────────────────────────────────────────────────
def inject_styles():
    st.markdown("""
    <style>
    .admin-hero {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 32px 40px;
        border-radius: 20px;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .admin-hero h2 { color: white; margin: 0 0 6px 0; font-size: 28px; }
    .admin-hero p  { color: #94a3b8; margin: 0; font-size: 15px; }

    .metric-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-card .val  { font-size: 32px; font-weight: 800; color: #38bdf8; }
    .metric-card .lbl  { font-size: 13px; color: #94a3b8; margin-top: 4px; }
    .metric-card .icon { font-size: 22px; margin-bottom: 8px; }

    .section-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 14px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1f2937;
    }

    .activity-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #1f2937;
    }
    .activity-item:last-child { border-bottom: none; }
    .activity-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #22c55e;
        margin-top: 5px;
        flex-shrink: 0;
    }
    .activity-text  { font-size: 13px; color: #e2e8f0; }
    .activity-time  { font-size: 11px; color: #64748b; margin-top: 2px; }

    .user-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-active   { background: #14532d; color: #4ade80; }
    .badge-inactive { background: #450a0a; color: #f87171; }
    .badge-admin    { background: #312e81; color: #a5b4fc; }

    .tab-content { padding-top: 16px; }
    </style>
    """, unsafe_allow_html=True)


# ── Helper: metric card ───────────────────────────────────────────────────────
def metric_card(icon, value, label):
    st.markdown(f"""
    <div class="metric-card">
        <div class="icon">{icon}</div>
        <div class="val">{value}</div>
        <div class="lbl">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Helper: format timestamp ──────────────────────────────────────────────────
def fmt_time(ts):
    if not ts:
        return "Never"
    try:
        dt = datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y  %H:%M")
    except:
        return str(ts)[:16]


# ── Main admin panel ──────────────────────────────────────────────────────────
def run():
    inject_styles()

    # Hero banner
    st.markdown("""
    <div class="admin-hero">
        <h2>🛠 Admin Control Panel</h2>
        <p>Manage users · Monitor usage · View analytics · Track activity</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "👥 User Management",
        "📈 Analytics",
        "🕒 Activity Feed"
    ])

    # ════════════════════════════════════════════════
    # TAB 1 — OVERVIEW
    # ════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        # Top metrics
        total_users  = database.get_user_count()
        active_users = database.get_active_user_count()
        total_usage  = database.get_total_usage()
        today_usage  = database.get_today_usage()

        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("👥", total_users,  "Total Users")
        with c2: metric_card("✅", active_users, "Active Users")
        with c3: metric_card("⚡", total_usage,  "Total API Calls")
        with c4: metric_card("📅", today_usage,  "Today's Usage")

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([3, 2])

        # Module usage bar chart
        with col_left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📊 Module Usage (All Time)</div>', unsafe_allow_html=True)

            usage_counts = database.get_module_usage_counts()

            if usage_counts:
                df_mod = pd.DataFrame(
                    list(usage_counts.items()),
                    columns=["Module", "Uses"]
                ).sort_values("Uses", ascending=True)

                fig = px.bar(
                    df_mod, x="Uses", y="Module",
                    orientation="h",
                    color="Uses",
                    color_continuous_scale="teal",
                    template="plotly_dark"
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=280,
                    showlegend=False,
                    coloraxis_showscale=False,
                )
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No usage data yet. Users need to use the modules first.")

            st.markdown('</div>', unsafe_allow_html=True)

        # Top users
        with col_right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏆 Top Users</div>', unsafe_allow_html=True)

            top_users = database.get_usage_by_user(limit=8)

            if top_users:
                df_top = pd.DataFrame(top_users, columns=["User", "Uses"])
                fig2 = px.pie(
                    df_top, names="User", values="Uses",
                    hole=0.5,
                    color_discrete_sequence=px.colors.sequential.Teal,
                    template="plotly_dark"
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=280,
                    legend=dict(font=dict(size=10)),
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No usage data yet.")

            st.markdown('</div>', unsafe_allow_html=True)

        # Recent activity preview
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕒 Recent Activity (Last 5)</div>', unsafe_allow_html=True)

        recent = database.get_recent_activity(limit=5)
        if recent:
            for row in recent:
                username, action, detail, ts = row
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-dot"></div>
                    <div>
                        <div class="activity-text">
                            <b>{username}</b> — {action}
                            {"<span style='color:#64748b'> · " + detail + "</span>" if detail else ""}
                        </div>
                        <div class="activity-time">🕐 {fmt_time(ts)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activity logged yet.")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # TAB 2 — USER MANAGEMENT
    # ════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        # ── Add New User ──────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">➕ Add New User</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([3, 3, 3, 1.5])
        with col1:
            new_username = st.text_input("Username", key="admin_new_user",
                                         placeholder="Enter username")
        with col2:
            new_pass = st.text_input("Password", type="password",
                                      key="admin_new_pass",
                                      placeholder="Enter password")
        with col3:
            new_pass2 = st.text_input("Confirm Password", type="password",
                                       key="admin_new_pass2",
                                       placeholder="Confirm password")
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Add User", use_container_width=True):
                if not new_username or not new_pass:
                    st.error("Username and password required.")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 4:
                    st.error("Password must be 4+ characters.")
                else:
                    ok = database.register_user(new_username.strip(), new_pass.strip())
                    if ok:
                        database.log_activity("admin", "Added User", f"Created account: {new_username}")
                        st.success(f"✅ User '{new_username}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Username already exists.")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Users Table ────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👥 All Users</div>', unsafe_allow_html=True)

        users_details = [u for u in database.get_all_users_details() if u[0] is not None]

        if users_details:
            # Search filter
            search = st.text_input("🔍 Search user", placeholder="Type username...", key="user_search")

            filtered = [u for u in users_details
                        if search.lower() in u[0].lower()] if search else users_details

            st.markdown(f"Showing **{len(filtered)}** of **{len(users_details)}** users")
            st.markdown("---")

            for row in filtered:
                username, created_at, last_login, is_active, total_uses = row

                col1, col2, col3, col4, col5, col6 = st.columns([2.5, 2.5, 2.5, 1.5, 1.5, 1.5])

                with col1:
                    badge = "badge-admin" if username == "admin" else \
                            "badge-active" if is_active else "badge-inactive"
                    label = "👑 Admin" if username == "admin" else \
                            "Active" if is_active else "Inactive"
                    st.markdown(f"""
                    <div style="padding-top:6px;">
                        <b style="color:#e2e8f0;">{username}</b><br>
                        <span class="user-badge {badge}">{label}</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"<div style='padding-top:8px;font-size:12px;color:#94a3b8;'>📅 Joined<br><span style='color:#e2e8f0'>{fmt_time(created_at)}</span></div>", unsafe_allow_html=True)

                with col3:
                    st.markdown(f"<div style='padding-top:8px;font-size:12px;color:#94a3b8;'>🔐 Last Login<br><span style='color:#e2e8f0'>{fmt_time(last_login)}</span></div>", unsafe_allow_html=True)

                with col4:
                    st.markdown(f"<div style='padding-top:8px;font-size:12px;color:#94a3b8;'>⚡ Total Uses<br><span style='color:#38bdf8;font-weight:700;font-size:16px'>{total_uses}</span></div>", unsafe_allow_html=True)

                with col5:
                    if username != "admin":
                        st.markdown("<br>", unsafe_allow_html=True)
                        toggle_label = "🔴 Deactivate" if is_active else "🟢 Activate"
                        if st.button(toggle_label, key=f"toggle_{username}", use_container_width=True):
                            database.toggle_user_active(username, not is_active)
                            action = "Deactivated" if is_active else "Activated"
                            database.log_activity("admin", f"{action} User", username)
                            st.rerun()

                with col6:
                    if username != "admin":
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("❌ Delete", key=f"del_{username}", use_container_width=True):
                            database.delete_user(username)
                            database.log_activity("admin", "Deleted User", username)
                            st.success(f"Deleted {username}")
                            st.rerun()

                st.markdown("<hr style='border-color:#1f2937;margin:6px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No users found.")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Reset Password ─────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔑 Reset User Password</div>', unsafe_allow_html=True)

        all_usernames = [u[0] for u in users_details if u[0] not in (None, "admin")] if users_details else []

        if all_usernames:
            col1, col2, col3 = st.columns([3, 3, 2])
            with col1:
                reset_user = st.selectbox("Select User", all_usernames, key="reset_user")
            with col2:
                reset_pass = st.text_input("New Password", type="password", key="reset_pass")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔑 Reset Password", use_container_width=True):
                    if reset_pass and len(reset_pass) >= 4:
                        database.change_user_password(reset_user, reset_pass)
                        database.log_activity("admin", "Reset Password", f"For user: {reset_user}")
                        st.success(f"✅ Password reset for '{reset_user}'")
                    else:
                        st.error("Password must be 4+ characters.")
        else:
            st.info("No users available for password reset.")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # TAB 3 — ANALYTICS
    # ════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        # Date range selector
        col1, col2 = st.columns([3, 1])
        with col2:
            days = st.selectbox("Time range", [7, 14, 30, 60, 90],
                                index=2, key="analytics_days",
                                format_func=lambda x: f"Last {x} days")

        # ── Daily usage trend ─────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Daily Usage Trend</div>', unsafe_allow_html=True)

        daily_data = database.get_usage_by_day(days=days)

        if daily_data:
            df_daily = pd.DataFrame(daily_data, columns=["Date", "Count"])
            df_daily["Date"] = pd.to_datetime(df_daily["Date"])

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_daily["Date"], y=df_daily["Count"],
                mode="lines+markers",
                line=dict(color="#38bdf8", width=2.5),
                marker=dict(size=6, color="#38bdf8"),
                fill="tozeroy",
                fillcolor="rgba(56,189,248,0.1)"
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                height=260,
                xaxis=dict(showgrid=False, color="#64748b"),
                yaxis=dict(gridcolor="#1f2937", color="#64748b"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No usage data yet for this period.")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Module breakdown ──────────────────────────
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🥧 Module Share</div>', unsafe_allow_html=True)

            usage_counts = database.get_module_usage_counts()
            if usage_counts:
                df_pie = pd.DataFrame(list(usage_counts.items()), columns=["Module", "Uses"])
                fig3 = px.pie(
                    df_pie, names="Module", values="Uses",
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    template="plotly_dark"
                )
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=300,
                    legend=dict(font=dict(size=9), orientation="v"),
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No module usage data yet.")

            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏆 Top 10 Users by Usage</div>', unsafe_allow_html=True)

            top_users = database.get_usage_by_user(limit=10)
            if top_users:
                df_usr = pd.DataFrame(top_users, columns=["User", "Uses"])
                fig4 = px.bar(
                    df_usr, x="Uses", y="User",
                    orientation="h",
                    color="Uses",
                    color_continuous_scale="Blues",
                    template="plotly_dark"
                )
                fig4.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=300,
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No user data yet.")

            st.markdown('</div>', unsafe_allow_html=True)

        # ── Raw usage table ───────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Recent API Calls Log</div>', unsafe_allow_html=True)

        recent_usage = database.get_recent_usage(limit=20)
        if recent_usage:
            df_log = pd.DataFrame(
                recent_usage,
                columns=["User", "Module", "Timestamp", "Status"]
            )
            df_log["Status"] = df_log["Status"].map(
                lambda s: f"{'✅' if s=='success' else '❌'} {s}"
            )
            df_log["Timestamp"] = df_log["Timestamp"].apply(fmt_time)
            st.dataframe(df_log, use_container_width=True, hide_index=True)
        else:
            st.info("No API call logs yet.")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # TAB 4 — ACTIVITY FEED
    # ════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        # Refresh button — uses session state to track last refresh time
        if "last_refresh" not in st.session_state:
            st.session_state["last_refresh"] = datetime.now().strftime("%H:%M:%S")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"<small style='color:#64748b;'>Last refreshed: {st.session_state['last_refresh']}</small>", unsafe_allow_html=True)
        with col2:
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_activity"):
                # Clear all activity feed records from DB
                try:
                    conn = database.connect_db()
                    conn.execute("DELETE FROM activity_feed")
                    conn.commit()
                    conn.close()
                except:
                    pass
                st.session_state["last_refresh"] = datetime.now().strftime("%H:%M:%S")
                st.rerun()

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕒 Live Activity Feed</div>', unsafe_allow_html=True)

        activities = database.get_recent_activity(limit=30)

        action_icons = {
            "Login":          "🔐",
            "Registered":     "🆕",
            "Added User":     "➕",
            "Deleted User":   "❌",
            "Deactivated User":"🔴",
            "Activated User": "🟢",
            "Reset Password": "🔑",
        }

        if activities:
            for row in activities:
                username, action, detail, ts = row
                icon = action_icons.get(action, "⚡")
                detail_html = f"<span style='color:#64748b;font-size:12px;'> — {detail}</span>" if detail else ""
                st.markdown(f"""
                <div class="activity-item">
                    <div style="font-size:20px;margin-top:2px;">{icon}</div>
                    <div style="flex:1;">
                        <div class="activity-text">
                            <b style="color:#38bdf8;">{username}</b>
                            &nbsp;·&nbsp; {action}
                            {detail_html}
                        </div>
                        <div class="activity-time">🕐 {fmt_time(ts)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activity recorded yet. Actions like login, register, and admin operations will appear here.")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


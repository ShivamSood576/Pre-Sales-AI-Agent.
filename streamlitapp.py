

import streamlit as st
import requests
import uuid
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Xicom AI Assistant",
    layout="wide"
)

# -----------------------------
# DEVICE-BASED SESSION ID
# -----------------------------
query_params = st.experimental_get_query_params()

if "session_id" in query_params:
    st.session_state.session_id = query_params["session_id"][0]
else:
    new_session_id = str(uuid.uuid4())
    st.session_state.session_id = new_session_id
    st.experimental_set_query_params(session_id=new_session_id)

# -----------------------------
# LOAD CHAT HISTORY FROM BACKEND (ONCE)
# -----------------------------
if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = True

    try:
        res = requests.get(
            f"{API_BASE}/admin/session/{st.session_state.session_id}",
            timeout=10
        )

        if res.status_code == 200:
            data = res.json()
            st.session_state.messages = data.get("messages", [])
            st.session_state.created_at = data.get("created_at")
            st.session_state.last_updated_at = data.get("last_updated_at")
        else:
            st.session_state.messages = []

    except Exception:
        st.session_state.messages = []

# -----------------------------
# ENSURE STATE KEYS EXIST
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "created_at" not in st.session_state:
    st.session_state.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if "last_updated_at" not in st.session_state:
    st.session_state.last_updated_at = st.session_state.created_at

# -----------------------------
# INITIAL GREETING (ONLY IF NO HISTORY)
# -----------------------------
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi 👋 Welcome to Xicom Technologies. How can I help you today?"
    })

# -----------------------------
# SIDEBAR
# -----------------------------
# st.sidebar.title("Xicom Admin Panel")

# st.sidebar.markdown("### 🕒 Session Info")
# st.sidebar.write("**Session ID:**", st.session_state.session_id)
# st.sidebar.write("**Started At:**", st.session_state.created_at)
# st.sidebar.write("**Last Active:**", st.session_state.last_updated_at)

page = st.sidebar.radio(
    "Navigate",
    ["💬 Chat", "📊 Admin – Sessions", "📄 Admin – Upload PDF"]
)

# =====================================================
# 💬 CHAT PAGE
# =====================================================
if page == "💬 Chat":
    st.title("💬 Xicom AI Chatbot")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        # update last activity
        st.session_state.last_updated_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        payload = {
            "question": user_input,
            "session_id": st.session_state.session_id
        }

        try:
            res = requests.post(
                f"{API_BASE}/chat",
                json=payload,
                timeout=30
            )
            data = res.json()
            bot_reply = data["answer"]

        except Exception:
            bot_reply = "⚠️ Unable to connect to server."

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply
        })

        with st.chat_message("assistant"):
            st.markdown(bot_reply)

# =====================================================
# 📊 ADMIN – SESSIONS
# =====================================================
elif page == "📊 Admin – Sessions":
    st.title("📊 All Chat Sessions")

    try:
        res = requests.get(f"{API_BASE}/admin/sessions_id", timeout=20)
        sessions = res.json().get("sessions", [])
    except Exception:
        st.error("❌ Unable to fetch sessions")
        st.stop()

    if not sessions:
        st.info("No sessions available.")
    else:
        for s in sessions:
            header = (
                f"🗂️ Session | "
                f"📅 Started: {s.get('created_at')} | "
                f"⏱️ Last Active: {s.get('last_updated_at')}"
            )

            with st.expander(header):
                st.write("🆔 **Session ID:**", s["session_id"])
                st.write("🎯 **Lead Type:**", s["lead_type"])
                st.write("👤 **Name:**", s["name"])
                st.write("📧 **Email:**", s["email"])
                st.write("📞 **Phone:**", s["phone"])
                st.write("📂 **Project Type:**", s["project_type"])
                st.write("🚀 **Business Goal:**", s["business_goal"])
                st.write("📦 **Total Projects:**", s.get("total_projects"))
                st.write("💬 **Message Count:**", s["message_count"])
                st.write("📝 **Last Message:**", s["last_message"])

                if st.button(
                    "View Full Conversation",
                    key=f"view_{s['session_id']}"
                ):
                    detail = requests.get(
                        f"{API_BASE}/admin/session/{s['session_id']}",
                        timeout=20
                    ).json()

                    st.subheader("🗨️ Conversation")
                    for m in detail["messages"]:
                        role = "🧑 User" if m["role"] == "user" else "🤖 Bot"
                        st.markdown(f"**{role}:** {m['content']}")

# =====================================================
# 📄 ADMIN – PDF UPLOAD
# =====================================================
elif page == "📄 Admin – Upload PDF":
    st.title("📄 Upload PDF to Knowledge Base")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        with st.spinner("Uploading & indexing PDF..."):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    "application/pdf"
                )
            }
            try:
                res = requests.post(
                    f"{API_BASE}/admin/upload-pdf",
                    files=files,
                    timeout=60
                )
                if res.status_code == 200:
                    st.success("✅ PDF uploaded and indexed successfully!")
                else:
                    st.error(res.text)
            except Exception:
                st.error("❌ Failed to upload PDF")

import streamlit as st
import requests
import os
from datetime import datetime

# ----------------------------
# CONFIG
# ----------------------------

st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="✉️",
    layout="wide"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ----------------------------
# MODERN UI CSS
# ----------------------------

st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #F9FAFB;
}

/* Header */
.main-title {
    text-align: center;
    font-size: 2.7rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 2rem;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 8px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 6px;
}

.policy { background:#E3F2FD; color:#0D47A1; }
.sensitive { background:#FFEBEE; color:#B71C1C; }
.general { background:#E8F5E9; color:#1B5E20; }
.clarification { background:#FFF3E0; color:#BF360C; }

/* Confidence */
.confidence {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    background: #F3F4F6;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# SESSION STATE
# ----------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------
# API FUNCTIONS
# ----------------------------

def check_api():
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except:
        return False


def process_email(message):
    try:
        r = requests.post(
            f"{API_BASE_URL}/process-email",
            json={
                "subject": "User Query",
                "body": message,
                "sender": "user@company.com",
                "recipient": None
            },
            timeout=30
        )
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


def get_badge(category):
    mapping = {
        "policy_query": ("📋 Policy", "policy"),
        "sensitive_matter": ("⚠️ Sensitive", "sensitive"),
        "general_inquiry": ("📧 General", "general"),
        "clarification_needed": ("❓ Clarification", "clarification"),
    }
    return mapping.get(category, ("📧 General", "general"))

# ----------------------------
# SIDEBAR
# ----------------------------

with st.sidebar:
    st.title("AI Email Assistant")

    st.markdown("---")

    st.subheader("🔌 API Status")
    if check_api():
        st.success("Connected")
    else:
        st.error("Disconnected")

    st.markdown("---")

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.caption("Built with LangChain + Gemini + RAG")

# ----------------------------
# MAIN CHAT UI
# ----------------------------

st.markdown("<div class='main-title'>AI Email Assistant</div>", unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask about company policies, HR matters, etc...")

if user_input:

    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Process via API
    with st.spinner("Analyzing with AI..."):
        response = process_email(user_input)

    if response:

        category = response.get("category", "general_inquiry")
        confidence = response.get("confidence_score", 0)
        draft = response.get("draft_reply", "No reply generated.")

        badge_text, badge_class = get_badge(category)

        assistant_message = f"""
<span class="badge {badge_class}">{badge_text}</span>
<span class="confidence">Confidence: {confidence:.0%}</span>

<br><br>

{draft}
"""

        if response.get("requires_human_review"):
            assistant_message += "\n\n🚨 *This email requires human review.*"

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        with st.chat_message("assistant"):
            st.markdown(assistant_message, unsafe_allow_html=True)

    else:
        st.error("Failed to connect to backend.")

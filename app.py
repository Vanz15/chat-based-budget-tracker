import streamlit as st
from db.connection import init_db, ensure_user
from agent.graph import run_agent

st.set_page_config(page_title="Budget Chat Tracker", page_icon="💸")

# --- Setup (runs on every load, cheap and idempotent) ---
init_db()

# Hardcoded single user for Phase 4 — replaced by real login in Phase 9
TEST_USER_ID = "test_user"
ensure_user(TEST_USER_ID)

from db.models import get_user_tone, set_user_tone

with st.sidebar:
    st.subheader("Settings")
    current_tone = get_user_tone(TEST_USER_ID)
    tone_options = ["neutral", "bubbly", "sarcastic", "coach", "snarky"]
    selected_tone = st.selectbox(
        "Comment tone", tone_options, index=tone_options.index(current_tone)
    )
    if selected_tone != current_tone:
        set_user_tone(TEST_USER_ID, selected_tone)
        st.rerun()

st.title("💸 Budget Chat Tracker")
st.caption("Prototype — Phase 4 (no login yet, single test user)")

# --- Chat history (session-only, resets on refresh for now) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Chat input ---
user_input = st.chat_input("Tell me what you bought, e.g. 'matcha PHP 220'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Logging..."):
            try:
                result = run_agent(TEST_USER_ID, user_input)
                response_text = result["response"]
            except Exception as e:
                response_text = f"Something went wrong: {e}"
            st.write(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
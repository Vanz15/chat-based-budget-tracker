import streamlit as st
from db.connection import init_db, ensure_user
from agent.graph import run_agent
import time

st.set_page_config(page_title="Cashually", page_icon="💸")

if not st.user.is_logged_in:
    st.title("💸 Cashually - Your Friendly Budget Chat Tracker Assistant")
    st.write("Please log in to continue.")
    if st.button("Log in with Google"):
        st.login()
    st.stop()

USER_ID = st.user.email

# --- Setup (runs on every load, cheap and idempotent) ---
init_db()

ensure_user(USER_ID)

from db.models import get_user_tone, set_user_tone

with st.sidebar:
    st.subheader("Settings")
    current_tone = get_user_tone(USER_ID)
    tone_options = ["neutral", "bubbly", "sarcastic", "coach", "snarky"]
    selected_tone = st.selectbox(
        "Comment tone", tone_options, index=tone_options.index(current_tone)
    )
    if selected_tone != current_tone:
        set_user_tone(USER_ID, selected_tone)
        st.rerun()
    st.divider()
    st.write(f"Logged in as {st.user.email}")
    if st.button("Log out"):
        st.logout()

st.title("💸 Cashually - Your Friendly Expense Tracker Assistant")
st.caption("Still under construction. Feel free to test it out. Enjoy budget tracking, cashually!")

# --- Chat history (session-only, resets on refresh for now) ---
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
    st.session_state.request_window_start = time.time()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_edit" not in st.session_state:
    st.session_state.pending_edit = None

if "pending_conversion" not in st.session_state:
    st.session_state.pending_conversion = None


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
        with st.spinner("Thinking..."):
            try:
                # Simple session-level rate guard (Groq free tier: ~30 req/min)
                now = time.time()
                if now - st.session_state.request_window_start > 60:
                    st.session_state.request_count = 0
                    st.session_state.request_window_start = now

                if st.session_state.request_count >= 25:
                    response_text = "I'm getting a lot of requests right now — give me about a minute and try again."
                else:
                    st.session_state.request_count += 1

                    if st.session_state.pending_conversion and user_input.replace(".", "", 1).isdigit():
                        from db.models import insert_transaction, get_user_tone
                        from llm.tone import generate_comment
                        conv = st.session_state.pending_conversion
                        php_amount = float(user_input)
                        insert_transaction(USER_ID, user_input, conv["item"], php_amount, conv["category"])
                        tone = get_user_tone(USER_ID)
                        try:
                            comment = generate_comment(conv["item"], php_amount, conv["category"], "PHP", tone)
                        except Exception:
                            comment = ""
                        response_text = f"Logged: {conv['item']} — ₱{php_amount:.2f} ({conv['category']})"
                        if comment:
                            response_text += f"\n\n{comment}"
                        st.session_state.pending_conversion = None
                    elif st.session_state.pending_edit and user_input.strip().lower() in ("yes", "y", "confirm"):
                        from db.models import update_transaction
                        edit = st.session_state.pending_edit
                        update_transaction(edit["transaction_id"], amount=edit["new_amount"], category=edit["new_category"])
                        response_text = "Updated!"
                        st.session_state.pending_edit = None
                    else:
                        result = run_agent(USER_ID, user_input)
                        response_text = result["response"]
                        if result.get("pending_conversion"):
                            st.session_state.pending_conversion = result["pending_conversion"]
                        if result.get("pending_edit"):
                            st.session_state.pending_edit = result["pending_edit"]
            except Exception as e:
                response_text = f"Something went wrong: {e}"
            st.write(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
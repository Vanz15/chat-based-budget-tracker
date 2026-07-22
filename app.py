import streamlit as st
from db.connection import init_db, ensure_user
from agent.graph import run_agent
from ui.styles import inject_custom_css
import time
from db.models import get_user_tone, set_user_tone, get_budget, get_month_spent
from llm.extraction import CATEGORIES

st.set_page_config(
    page_title="LastNa",
    page_icon="👀",
    layout="wide",
    initial_sidebar_state="expanded"
)


if not st.user.is_logged_in:
    st.title("LastNa 👀")
    st.write("Your free expense and budget tracker. Please log in to continue.")
    if st.button("Log in with Google"):
        st.login()
    st.stop()

USER_ID = st.user.email
init_db()
ensure_user(USER_ID)

inject_custom_css()


# --- Custom header ---
st.html("""
<div class="lastna-header">
    <h1>👀 LastNa <span class="beta-badge">Beta</span></h1>
    <p style="font-size:12px; color:var(--tertiary-text); margin:2px 0 0 0; font-style:italic;">
        Your last purchase was not your last. And we know. 😉
    </p>
</div>
""")

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="section-label">Tone</div>', unsafe_allow_html=True)
    current_tone = get_user_tone(USER_ID)
    tone_options = ["neutral", "bubbly", "sarcastic", "coach", "snarky"]
    selected_tone = st.selectbox(
        "Comment tone", tone_options, index=tone_options.index(current_tone),
        label_visibility="collapsed",
    )
    if selected_tone != current_tone:
        set_user_tone(USER_ID, selected_tone)
        st.rerun()

    st.markdown('<div class="section-label" style="margin-top:20px;">Budgets</div>', unsafe_allow_html=True)
    any_budget = False
    for cat in CATEGORIES:
        limit = get_budget(USER_ID, cat)
        if limit:
            any_budget = True
            spent = get_month_spent(USER_ID, cat)
            pct = min(spent / limit, 1.5) if limit else 0
            pct_display = min(pct * 100, 100)
            if pct >= 1.0:
                color, status = "var(--red)", "Over"
            elif pct >= 0.8:
                color, status = "var(--amber)", "Almost there"
            else:
                color, status = "var(--teal)", "On track"
            st.html(f"""
            <div style="margin-bottom: 14px;">
                <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:4px;">
                    <span style="font-weight:700; color:var(--navy);">{cat}</span>
                    <span style="color:{color}; font-weight:700; font-size:0.75rem;">{status}</span>
                </div>
                <div style="background:#EEF2F1; border-radius:8px; height:8px; overflow:hidden;">
                    <div style="background:{color}; width:{pct_display}%; height:100%; border-radius:8px;"></div>
                </div>
                <div style="font-size:0.78rem; color:var(--tertiary-text); margin-top:3px;">
                    ₱{spent:.0f} of ₱{limit:.0f}
                </div>
            </div>
            """)
    if not any_budget:
        st.caption("No budgets set yet — try 'set food budget to 3000'")

    st.html(f"""
    <div class="profile-row">
        <img src="{st.user.picture if hasattr(st.user, 'picture') else ''}" onerror="this.style.display='none'">
        <div style="flex:1;">
            <p class="name">{st.user.name if hasattr(st.user, 'name') else st.user.email}</p>
            <p class="status">Logged in</p>
        </div>
    </div>
    """)
    if st.button("Log out"):
        st.logout()

# --- Session state ---
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
    st.session_state.request_window_start = time.time()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_edit" not in st.session_state:
    st.session_state.pending_edit = None
if "pending_conversion" not in st.session_state:
    st.session_state.pending_conversion = None

# --- Empty state or chat history ---
if not st.session_state.messages:
     st.html("""
    <div class="empty-state">
        <div class="receipt-illustration">
            <div class="receipt-icon"><i class="ti ti-receipt"></i></div>
        </div>
        <h2>Let's track your spending</h2>
        <p>Tell me what you bought like you're texting a friend — I'll handle the rest. </p>
        <div class="prompt-grid">
            <button disabled>"matcha ₱220"</button>
            <button disabled>"set food budget to 3000"</button>
            <button disabled>"how much did I spend this week"</button>
            <button disabled>"actually that was ₱150"</button>
        </div>
    </div>
    """)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑"):
                st.html(f'<div class="user-bubble"><p>{msg["content"]}</p></div>')
        else:
            alert_class = ""
            if "over" in msg["content"].lower() and "budget" in msg["content"].lower():
                alert_class = "alert-danger"
            elif "heads up" in msg["content"].lower() or "almost" in msg["content"].lower():
                alert_class = "alert-warning"
            with st.chat_message("assistant", avatar="💸"):
                content_html = msg["content"].replace("\n", "<br>")
                st.html(f'<div class="assistant-bubble {alert_class}"><p>{content_html}</p></div>')

# --- Chat input ---
user_input = st.chat_input("Tell me what you bought, e.g. 'matcha ₱220'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        now = time.time()
        if now - st.session_state.request_window_start > 60:
            st.session_state.request_count = 0
            st.session_state.request_window_start = now

        if st.session_state.request_count >= 25:
            response_text = "I'm getting a lot of requests right now — give me about a minute and try again."
        else:
            st.session_state.request_count += 1

            if st.session_state.pending_conversion and user_input.replace(".", "", 1).isdigit():
                from db.models import insert_transaction
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

    st.session_state.messages.append({"role": "assistant", "content": response_text})

    if "budget set" in response_text.lower() or "logged:" in response_text.lower() or "updated!" in response_text.lower():
        st.rerun()
    else:
        st.rerun()
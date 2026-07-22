import streamlit as st


def inject_custom_css():
    st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1 {
        font-family: 'Fraunces', serif !important;
        font-weight: 700 !important;
        color: #1B2430 !important;
        letter-spacing: -0.02em;
    }

    /* Chat bubbles */
    .stChatMessage {
        border-radius: 14px;
        padding: 4px 6px;
        margin-bottom: 4px;
    }

    div[data-testid="stChatMessageContent"] {
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* User messages — coral receipt-style bubble */
    .stChatMessage:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #FFE8E4;
        border-left: 3px solid #FF6F59;
    }

    /* Assistant messages — mint bubble */
    .stChatMessage:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #E6F8F6;
        border-left: 3px solid #2EC4B6;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E4E9E7;
    }

    /* Buttons */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
    }

    /* Selectbox */
    div[data-baseweb="select"] {
        border-radius: 10px;
    }
    </style>
    """)


def budget_gauge(spent: float, limit: float, category: str):
    """Renders a small styled budget progress gauge in the sidebar."""
    pct = min(spent / limit, 1.5) if limit else 0
    pct_display = min(pct * 100, 100)

    if pct >= 1.0:
        color = "#E85D5D"
        status = "Over budget"
    elif pct >= 0.8:
        color = "#F4A340"
        status = "Almost there"
    else:
        color = "#2EC4B6"
        status = "On track"

    st.html(f"""
    <div style="margin-bottom: 12px;">
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#1B2430; margin-bottom:4px;">
            <span style="font-weight:600;">{category}</span>
            <span style="color:{color}; font-weight:600;">{status}</span>
        </div>
        <div style="background:#EEF2F1; border-radius:8px; height:10px; overflow:hidden;">
            <div style="background:{color}; width:{pct_display}%; height:100%; border-radius:8px; transition: width 0.3s;"></div>
        </div>
        <div style="font-size:0.78rem; color:#7C8B93; margin-top:3px;">
            ₱{spent:.0f} of ₱{limit:.0f}
        </div>
    </div>
    """)
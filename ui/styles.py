import streamlit as st


def inject_custom_css():
    """Inject custom CSS to match the LastNa Variant 1 design."""
    st.html(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;600;700&family=Inter:wght@400;500;600;700&display=swap');
  @import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont/tabler-icons.min.css');

  :root {
    --mint-white: #F4F7F5;
    --navy: #1B2430;
    --coral: #FF6F59;
    --coral-shadow: rgba(255, 111, 89, 0.2);
    --teal: #2EC4B6;
    --teal-soft: rgba(46, 196, 182, 0.1);
    --teal-ring: rgba(46, 196, 182, 0.4);
    --amber: #F4A340;
    --red: #E85D5D;
    --white: #FFFFFF;
    --secondary-text: #4A5568;
    --tertiary-text: #718096;
    --border: #E2E8F0;
    --radius-sm: 4px;
    --radius-md: 10px;
    --radius-lg: 16px;
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
    --shadow-md: 0 8px 24px rgba(27,36,48,0.08);
    --shadow-bubble: 0 4px 12px rgba(27,36,48,0.06);
  }
  

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--navy);
  }

  h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--navy) !important;
    letter-spacing: -0.02em;
  }

  /* Main app background */
  .stApp {
    background-color: var(--mint-white);
  }

  /* Hide Streamlit's default header/footer */
  footer {
    display: none !important;
  }

  /* Keep Streamlit header container alive */
  header[data-testid="stHeader"] {
    background: transparent !important;
  }

  /* Ensure sidebar collapsed control is always visible and clickable */
  [data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 16px !important;
    left: 16px !important;
    z-index: 999999 !important;
  }
  [data-testid="stSidebarCollapsedControl"] button {
    background: var(--white) !important;
    color: var(--navy) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-sm) !important;
    width: 40px !important;
    height: 40px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  [data-testid="stSidebarCollapsedControl"] button:hover {
    background: var(--mint-white) !important;
    color: var(--coral) !important;
    border-color: var(--coral) !important;
  }
  [data-testid="stSidebarCollapsedControl"] svg {
    width: 22px !important;
    height: 22px !important;
  }


  /* Custom header */
  .lastna-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    padding: 0 24px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .lastna-header h1 {
    font-size: 24px;
    margin: 0;
  }
  .lastna-header .beta-badge {
    display: inline-block;
    margin-left: 10px;
    padding: 3px 7px;
    background: var(--teal-soft);
    color: var(--teal);
    font-size: 10px;
    font-weight: 700;
    border-radius: 6px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'Inter', sans-serif;
  }

  /* Empty state */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 20px;
  }
  .empty-state h2 {
    font-size: 40px;
    margin-bottom: 12px;
  }
  .empty-state p {
    color: var(--secondary-text);
    font-size: 17px;
    max-width: 460px;
    margin-bottom: 28px;
  }
  .receipt-illustration {
    position: relative;
    margin-bottom: 32px;
  }
  .receipt-illustration img {
    width: 240px;
    height: 240px;
    object-fit: cover;
    border-radius: 2.5rem;
    box-shadow: var(--shadow-md);
    transform: rotate(3deg);
  }
  .receipt-icon {
    position: absolute;
    bottom: -16px;
    right: -16px;
    background: var(--white);
    padding: 14px;
    border-radius: 18px;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
    transform: rotate(-6deg);
  }
  .receipt-icon i {
    font-size: 30px;
    color: var(--coral);
  }
  .prompt-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    width: 100%;
    max-width: 420px;
  }
  @media (min-width: 640px) {
    .prompt-grid {
      grid-template-columns: 1fr 1fr;
    }
  }
  .prompt-grid button {
    padding: 14px 22px;
    background: var(--white);
    border: 2px solid var(--border);
    border-radius: var(--radius-lg);
    color: var(--navy);
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-sm);
    font-family: 'Inter', sans-serif;
  }
  .prompt-grid button:hover {
    border-color: var(--coral);
    color: var(--coral);
  }

  /* Chat thread container */
  .stChatMessage {
    background: transparent !important;
    padding: 0 !important;
    margin-bottom: 28px !important;
  }
  .stChatMessage .stChatMessageContent {
    padding: 0;
  }
  .stChatMessageAvatar {
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    min-height: 40px !important;
    border-radius: 50% !important;
    border: 2px solid var(--white) !important;
    box-shadow: var(--shadow-sm) !important;
    background: transparent !important;
  }
  .stChatMessageAvatar > div {
    width: 100% !important;
    height: 100% !important;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Assistant avatar pulse */
  .assistant-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--teal);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid var(--white);
    box-shadow: 0 0 0 0 rgba(46, 196, 182, 0.4);
    animation: avatar-pulse 2s infinite;
  }
  @keyframes avatar-pulse {
    0% { box-shadow: 0 0 0 0 rgba(46, 196, 182, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(46, 196, 182, 0); }
    100% { box-shadow: 0 0 0 0 rgba(46, 196, 182, 0); }
  }

  /* Assistant message bubble - receipt style */
  .assistant-bubble {
    position: relative;
    background: var(--white);
    color: var(--navy);
    border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm);
    padding: 18px 20px;
    box-shadow: var(--shadow-bubble);
    border: 1px solid var(--border);
    font-size: 15px;
    line-height: 1.55;
    max-width: 100%;
  }
  .assistant-bubble::after {
    content: "";
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 100%;
    height: 8px;
    background-image:
      linear-gradient(135deg, var(--white) 25%, transparent 25%),
      linear-gradient(225deg, var(--white) 25%, transparent 25%);
    background-position: left bottom;
    background-repeat: repeat-x;
    background-size: 12px 12px;
    filter: drop-shadow(0 4px 2px rgba(27,36,48,0.03));
  }
  .assistant-bubble.alert-warning {
    border: 2px solid var(--amber);
  }
  .assistant-bubble.alert-danger {
    border: 2px solid var(--red);
  }
  .assistant-bubble p {
    margin: 0;
  }
  .assistant-status {
    margin-top: 10px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Inter', sans-serif;
  }
  .alert-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  /* User message bubble */
  .user-bubble {
    background: var(--coral);
    color: var(--white);
    border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg);
    padding: 16px 18px;
    box-shadow: 0 4px 14px var(--coral-shadow);
    font-size: 15px;
    line-height: 1.55;
  }
  .user-bubble p {
    margin: 0;
  }

  /* Chat input area */
  .stChatInputContainer {
    background: rgba(244, 247, 245, 0.95) !important;
    backdrop-filter: blur(4px);
    border-top: 1px solid var(--border);
    padding: 16px 0;
  }
  .stChatInputContainer textarea {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    color: var(--navy) !important;
    background: var(--white) !important;
  }
  .stChatInputContainer textarea::placeholder {
    color: var(--tertiary-text) !important;
  }
  .stChatInputContainer button {
    background: var(--coral) !important;
    color: var(--white) !important;
    border-radius: var(--radius-md) !important;
    transition: transform 0.15s ease;
  }
  .stChatInputContainer button:hover {
    transform: translateY(-2px);
  }

  /* Sidebar styling */
  section[data-testid="stSidebar"] {
    background-color: var(--white);
    border-left: 1px solid var(--border);
    max-width: 320px;
    min-width: 0; 
  }
  section[data-testid="stSidebar"] > div {
    padding-top: 0;
  }
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    font-family: 'Fraunces', serif;
  }
  section[data-testid="stSidebar"] .stSelectbox > div > div {
    border-radius: var(--radius-md);
    border-color: var(--border);
  }
  /* Sidebar sizing */
  /* Responsive sidebar */
  section[data-testid="stSidebar"] {
    background-color: var(--white);
    border-left: 1px solid var(--border);
    width: 320px !important;
  }

  section[data-testid="stSidebar"] > div {
    width: 320px !important;
    padding-top: 0;
  }


  /* Tone selector */
  .tone-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    background: var(--mint-white);
    padding: 6px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    margin-bottom: 8px;
  }
  .tone-btn {
    flex: 1 1 auto;
    padding: 8px 10px;
    border-radius: 8px;
    border: none;
    background: transparent;
    color: var(--tertiary-text);
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
    font-family: 'Inter', sans-serif;
  }
  .tone-btn.active {
    background: var(--white);
    color: var(--navy);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
  }
  .tone-btn:not(.active):hover {
    background: rgba(255,255,255,0.5);
    color: var(--navy);
  }

  /* Section labels */
  .section-label {
    font-size: 11px;
    font-weight: 800;
    color: var(--tertiary-text);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 12px;
    font-family: 'Inter', sans-serif;
  }

  /* Period badge */
  .period-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    color: var(--teal);
    background: var(--teal-soft);
    padding: 3px 8px;
    border-radius: 6px;
    letter-spacing: 0.02em;
    font-family: 'Inter', sans-serif;
  }

  /* User profile row */
  .profile-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 4px;
    border-top: 1px solid var(--border);
    background: rgba(244, 247, 245, 0.3);
  }
  .profile-row img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 2px solid var(--white);
    box-shadow: var(--shadow-sm);
    object-fit: cover;
  }
  .profile-row .name {
    font-size: 14px;
    font-weight: 700;
    color: var(--navy);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .profile-row .status {
    font-size: 10px;
    font-weight: 600;
    color: var(--tertiary-text);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
  }
  .profile-row button {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--tertiary-text);
    padding: 6px;
    transition: color 0.2s ease;
  }
  .profile-row button:hover {
    color: var(--red);
  }

  /* Scrollbar */
  ::-webkit-scrollbar {
    width: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #CBD5E1;
  }
  button[data-testid="stSidebarCollapseButton"],
  [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: var(--navy) !important;
  }

  /* Mobile responsiveness */
  @media (max-width: 768px) {
    .lastna-header {
      padding: 0 16px;
    }
    .empty-state {
      padding: 40px 16px;
    }
    .empty-state h2 {
      font-size: 30px;
    }
    .receipt-illustration img {
      width: 180px;
      height: 180px;
    }
  }
/* Ensure sidebar toggle remains accessible */
 button[data-testid="stSidebarCollapseButton"],
 [data-testid="collapsedControl"] {
     display: flex !important;
     visibility: visible !important;
     opacity: 1 !important;
-    color: var(--navy) !important;
+    color: var(--navy) !important;
+    /* make sure the button is on top of the header when collapsed */
+    z-index: 9999 !important;


</style>
        """
    )

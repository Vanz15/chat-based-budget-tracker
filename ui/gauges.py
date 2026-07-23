"""Budget gauge components for LastNa."""
import streamlit as st


def semi_circular_gauge(spent: float, limit: float, category: str) -> str:
    """
    Render a responsive semi-circular SVG budget gauge.

    Args:
        spent: Amount already spent.
        limit: Budget limit for the category.
        category: Display name for the budget category.

    Returns:
        HTML string for the gauge.
    """
    pct = spent / limit if limit else 0
    pct_display = min(round(pct * 100), 150)

    if pct >= 1.0:
        color = "#E85D5D"
        status_color = "#E85D5D"
    elif pct >= 0.8:
        color = "#F4A340"
        status_color = "#F4A340"
    else:
        color = "#2EC4B6"
        status_color = "#718096"

    # Arc length for semi-circle radius 40 is ~126 units
    arc_length = 126
    fill_length = min(pct, 1.0) * arc_length
    offset = arc_length - fill_length

    return f"""
    <div style="width:100%;min-height:170px;display:flex;flex-direction:column;align-items:center;margin-bottom:1.25rem;">
      <div style="position:relative;width:140px;height:80px;">
        <svg viewBox="0 0 100 60" width="140" height="80" style="display:block;">
          <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#F4F7F5" stroke-linecap="round" stroke-width="8"/>
          <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{color}" stroke-dasharray="{arc_length}" stroke-dashoffset="{offset}" stroke-linecap="round" stroke-width="8"/>
        </svg>
        <div style="position:absolute;bottom:2px;left:0;right:0;text-align:center;">
          <span style="font-family:'Fraunces',serif;font-size:1.4rem;font-weight:700;color:#1B2430;">{pct_display}%</span>
        </div>
      </div>
      <div style="text-align:center;margin-top:4px;">
        <span style="display:block;font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:700;color:#1B2430;">{category}</span>
        <span style="font-family:'Inter',sans-serif;font-size:0.8rem;font-weight:600;color:{status_color};">₱{spent:,.0f} / ₱{limit:,.0f}</span>
      </div>
    </div>
    """


def budget_gauge_bar(spent: float, limit: float, category: str) -> None:
    """Render a compact horizontal budget bar (fallback/mobile view)."""
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
    <div style="margin-bottom:clamp(0.75rem, 2vw, 1rem);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
        <span style="font-family:'Inter',sans-serif;font-size:clamp(0.8rem, 2vw, 0.9rem);font-weight:600;color:#1B2430;">{category}</span>
        <span style="font-family:'Inter',sans-serif;font-size:clamp(0.65rem, 1.6vw, 0.75rem);font-weight:700;color:{color};">{status}</span>
      </div>
      <div style="background:#EEF2F1;border-radius:8px;height:clamp(8px, 1.5vw, 10px);overflow:hidden;">
        <div style="background:{color};width:{pct_display}%;height:100%;border-radius:8px;transition:width 0.5s ease;"></div>
      </div>
      <div style="font-family:'Inter',sans-serif;font-size:clamp(0.65rem, 1.6vw, 0.75rem);color:#718096;margin-top:0.25rem;">
        ₱{spent:,.0f} of ₱{limit:,.0f}
      </div>
    </div>
    """)

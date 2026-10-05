"""
AI Travel Itinerary Generator — Streamlit UI.

Run from the project folder:
    streamlit run app.py
"""

import streamlit as st

from recommendation_engine import generate_itinerary, itinerary_as_text
from travel_data import SUPPORTED_DESTINATIONS

st.set_page_config(
    page_title="AI Travel Itinerary Generator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Visual theme: cream canvas, teal accents, rounded cards
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #f6f1e7 0%, #fbfaf6 42%, #e7f3f0 100%);
    }

    [data-testid="stHeader"] { background: transparent; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f3d3e 0%, #1a5c5e 55%, #1f6f64 100%);
    }
    [data-testid="stSidebar"] * {
        color: #f4f7f6 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #e8f4f2 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] input {
        background-color: rgba(255,255,255,0.12) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
    }

    .hero-wrap {
        background: linear-gradient(120deg, rgba(15,61,62,0.92), rgba(31,111,100,0.88)),
                    url('https://images.unsplash.com/photo-1526772662000-3f88f10405ff?auto=format&fit=crop&w=1600&q=60');
        background-size: cover;
        background-position: center;
        border-radius: 28px;
        padding: 2.4rem 2.6rem;
        color: #fff;
        box-shadow: 0 18px 40px rgba(15, 61, 62, 0.18);
        margin-bottom: 1.4rem;
    }
    .hero-kicker {
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-size: 0.78rem;
        opacity: 0.86;
        margin-bottom: 0.4rem;
    }
    .hero-title {
        font-family: 'Source Serif 4', serif;
        font-size: 2.45rem;
        line-height: 1.15;
        margin: 0 0 0.45rem 0;
    }
    .hero-sub {
        font-size: 1.2rem;
        font-weight: 600;
        color: #b7eadb;
        margin-bottom: 0.55rem;
    }
    .hero-desc { max-width: 640px; opacity: 0.92; }

    .chip-row { display: flex; flex-wrap: wrap; gap: 0.45rem; margin: 0.4rem 0 1rem 0; }
    .chip {
        background: #ffffff;
        border: 1px solid #d7ebe6;
        color: #1a5c5e;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 500;
    }

    .metric-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.05rem 1.15rem;
        border: 1px solid #e4efe9;
        box-shadow: 0 10px 24px rgba(26, 92, 94, 0.06);
        min-height: 108px;
    }
    .metric-label { color: #6b7c78; font-size: 0.8rem; letter-spacing: 0.04em; text-transform: uppercase; }
    .metric-value { color: #143c3d; font-size: 1.22rem; font-weight: 700; margin-top: 0.35rem; }

    .day-card {
        background: #ffffff;
        border-radius: 22px;
        padding: 1.25rem 1.35rem 1.1rem 1.35rem;
        border: 1px solid #e4efe9;
        box-shadow: 0 12px 28px rgba(26, 92, 94, 0.07);
        margin-bottom: 1rem;
    }
    .day-head {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        border-bottom: 2px solid #d8efe9;
        padding-bottom: 0.55rem;
        margin-bottom: 0.9rem;
    }
    .day-title {
        font-family: 'Source Serif 4', serif;
        font-size: 1.45rem;
        color: #143c3d;
        margin: 0;
    }
    .slot-block { margin: 0.85rem 0; }
    .slot-label { font-weight: 650; color: #1f6f64; margin-bottom: 0.15rem; }
    .place-name { font-size: 1.08rem; color: #1b2e2e; font-weight: 600; }
    .muted { color: #5f736f; font-size: 0.92rem; }
    .day-total {
        background: #eef7f4;
        color: #145c56;
        border-radius: 12px;
        padding: 0.55rem 0.8rem;
        font-weight: 650;
        margin-top: 0.6rem;
    }

    .section-title {
        font-family: 'Source Serif 4', serif;
        color: #143c3d;
        font-size: 1.7rem;
        margin: 1.4rem 0 0.6rem 0;
    }
    .soft-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.1rem 1.2rem;
        border: 1px solid #e4efe9;
        box-shadow: 0 8px 20px rgba(26, 92, 94, 0.05);
        height: 100%;
    }
    .tip-item, .pack-item {
        padding: 0.45rem 0;
        border-bottom: 1px dashed #dce8e4;
        color: #2c3f3d;
    }

    .error-box {
        background: #fff6ee;
        border: 1px solid #f0d3b8;
        color: #6b3f1f;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #1f6f64, #2a9d8f);
        color: white;
        border: 0;
        border-radius: 14px;
        padding: 0.6rem 1rem;
        font-weight: 650;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #185851, #21867a);
        color: white;
        border: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def rupees(amount):
    return f"₹{int(amount):,}"


def render_hero():
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-kicker">Student portfolio · rule-based planner</div>
            <h1 class="hero-title">✈️ AI Travel Itinerary Generator</h1>
            <div class="hero-sub">Plan smarter. Travel better.</div>
            <p class="hero-desc">
                Create a personalized day-by-day travel plan based on your interests,
                budget, travel style and available time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    chips = "".join(f'<span class="chip">{city}</span>' for city in SUPPORTED_DESTINATIONS)
    st.markdown(f'<div class="chip-row">{chips}</div>', unsafe_allow_html=True)


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_day_card(day):
    # Build HTML without leading indentation. Streamlit markdown treats
    # 4+ space-indented lines as a code block, which would show tags as text.
    slots_html = []
    for slot in day["slots"]:
        note = f'<div class="muted">{slot.get("note")}</div>' if slot.get("note") else ""
        hours = slot.get("duration_hours", 1)
        hour_label = "hour" if hours == 1 else "hours"
        slots_html.append(
            '<div class="slot-block">'
            f'<div class="slot-label">{slot["emoji"]} {slot["slot"]}</div>'
            f'<div class="place-name">{slot["name"]}</div>'
            f'<div class="muted">Category: {slot["category"]} · Duration: {hours:g} {hour_label}</div>'
            f'<div class="muted">Estimated Cost: {rupees(slot.get("display_cost", slot["estimated_cost"]))}</div>'
            f"{note}"
            "</div>"
        )
    body = "".join(slots_html)
    html = (
        '<div class="day-card">'
        '<div class="day-head">'
        f'<h3 class="day-title">DAY {day["day"]}</h3>'
        '<span class="muted">Personalized schedule</span>'
        "</div>"
        f"{body}"
        f'<div class="day-total">💰 Day {day["day"]} Estimated Cost: {rupees(day["estimated_cost"])}</div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def sidebar_preferences():
    st.sidebar.markdown("### 🧳 Trip Preferences")
    st.sidebar.caption("Tune the plan, then generate a day-by-day itinerary.")

    destination = st.sidebar.text_input(
        "Destination",
        placeholder="e.g. Bengaluru",
        help="Type a city. Supported catalogue: major Indian destinations listed on the home page.",
    )
    num_days = st.sidebar.slider("Number of days", min_value=1, max_value=7, value=3)
    budget = st.sidebar.radio("Budget", ["Low", "Medium", "High"], index=1, horizontal=True)
    travel_type = st.sidebar.selectbox("Travel type", ["Solo", "Couple", "Family", "Friends"])
    interests = st.sidebar.multiselect(
        "Interests",
        ["Adventure", "Culture", "Food", "Nature", "Shopping", "History", "Relaxation", "Nightlife"],
        default=["Culture", "Food", "Nature"],
    )
    travel_pace = st.sidebar.radio("Travel pace", ["Relaxed", "Balanced", "Packed"], index=1)
    generate = st.sidebar.button("✨ Generate My Itinerary", type="primary")
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Recommendations are produced by a local rule-based engine. "
        "No API keys and no generative AI calls are required."
    )
    return {
        "destination": destination,
        "num_days": num_days,
        "budget": budget,
        "travel_type": travel_type,
        "interests": interests,
        "travel_pace": travel_pace,
        "generate": generate,
    }


def render_itinerary(result):
    st.markdown('<h2 class="section-title">Your Personalized Itinerary ✨</h2>', unsafe_allow_html=True)
    st.caption(f"{result['destination']}, {result['state']} — {result['tagline']}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("📍 Destination", result["destination"])
    with c2:
        metric_card("📅 Number of Days", str(result["num_days"]))
    with c3:
        metric_card("💰 Estimated Budget", rupees(result["grand_total"]))
    with c4:
        interest_text = ", ".join(result["interests"]) if result["interests"] else "All-rounder mix"
        metric_card("❤️ Interests", interest_text)

    st.markdown("")
    for day in result["days"]:
        render_day_card(day)

    st.markdown('<h2 class="section-title">Travel Summary</h2>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        metric_card("Total estimated cost", rupees(result["grand_total"]))
    with s2:
        metric_card("Number of places", str(result["place_count"]))
    with s3:
        covered = ", ".join(result["interests_covered"]) if result["interests_covered"] else "—"
        metric_card("Interests covered", covered)
    with s4:
        metric_card("Approx. daily budget", rupees(result["average_daily"]))

    left, right = st.columns(2)
    with left:
        st.markdown('<h2 class="section-title">Smart Travel Tips</h2>', unsafe_allow_html=True)
        tips_html = "".join(f'<div class="tip-item">💡 {tip}</div>' for tip in result["tips"])
        st.markdown(f'<div class="soft-card">{tips_html}</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<h2 class="section-title">Packing Checklist</h2>', unsafe_allow_html=True)
        pack_html = "".join(f'<div class="pack-item">☑️ {item}</div>' for item in result["packing"])
        st.markdown(f'<div class="soft-card">{pack_html}</div>', unsafe_allow_html=True)

    st.download_button(
        "⬇️ Download itinerary (.txt)",
        data=itinerary_as_text(result),
        file_name=f"{result['destination'].lower()}-itinerary.txt",
        mime="text/plain",
    )

    with st.expander("How this itinerary was built (rule-based, not a generative AI API)"):
        st.markdown(
            """
            1. **Filter** attractions for the chosen city.
            2. **Match** categories to your interests (Nature, Food, History, and so on).
            3. **Respect budget** by capping expensive activities on Low/Medium plans.
            4. **Respect travel type** — for example families skip late-night club scenes.
            5. **Respect pace** — Relaxed fills two slots; Balanced and Packed fill three.
            6. **Schedule** morning / afternoon / evening without repeating the same place.
            7. **Price** each day, then sum a trip total with a budget multiplier.
            """
        )


def main():
    prefs = sidebar_preferences()
    render_hero()

    if "itinerary" not in st.session_state:
        st.session_state.itinerary = None
        st.session_state.error = None

    if prefs["generate"]:
        if not prefs["destination"].strip():
            st.session_state.itinerary = None
            st.session_state.error = "Please enter a destination to generate your plan."
        else:
            result = generate_itinerary(
                destination_input=prefs["destination"],
                num_days=prefs["num_days"],
                budget=prefs["budget"],
                travel_type=prefs["travel_type"],
                interests=prefs["interests"],
                travel_pace=prefs["travel_pace"],
            )
            if result["ok"]:
                st.session_state.itinerary = result
                st.session_state.error = None
            else:
                st.session_state.itinerary = None
                st.session_state.error = result["error"]

    if st.session_state.error:
        st.markdown(f'<div class="error-box">⚠️ {st.session_state.error}</div>', unsafe_allow_html=True)
    elif st.session_state.itinerary:
        render_itinerary(st.session_state.itinerary)
    else:
        st.markdown(
            """
            <div class="soft-card">
                <p><strong>Ready when you are.</strong> Use the sidebar to describe your trip,
                then click <em>Generate My Itinerary</em>.</p>
                <p class="muted">
                    Tip for demos: try Bengaluru · 3 days · Medium budget · Couple ·
                    Culture + Food + Nature · Balanced pace.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

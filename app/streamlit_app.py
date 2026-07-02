import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generation"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "embeddings"))
from pinecone_search import search
from answer_question import answer, answer_free

# ---------- Page config ----------
st.set_page_config(page_title="AI Time Capsule & Trend Oracle", page_icon="🕰️", layout="centered")

# ---------- Era themes ----------
def get_theme(year: int):
    if year <= 2017:
        return {
            "bg": "linear-gradient(135deg, #2c3e50, #4ca1af)",
            "accent": "#4ca1af",
            "era": "📻 2015–2017 · Flat Design Era",
            "emoji": "📻",
        }
    elif year <= 2019:
        return {
            "bg": "linear-gradient(135deg, #f7971e, #ffd200)",
            "accent": "#f7971e",
            "era": "🌍 2018–2019 · Pre-Pandemic World",
            "emoji": "🌍",
        }
    elif year <= 2021:
        return {
            "bg": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
            "accent": "#cc00ff",
            "era": "😷 2020–2021 · Lockdown Era",
            "emoji": "😷",
        }
    elif year <= 2023:
        return {
            "bg": "linear-gradient(135deg, #232526, #414345)",
            "accent": "#74ebd5",
            "era": "🔄 2022–2023 · Recovery & Reset",
            "emoji": "🔄",
        }
    else:
        return {
            "bg": "linear-gradient(135deg, #000428, #004e92)",
            "accent": "#00d4ff",
            "era": "🤖 2024–2026 · AI Acceleration",
            "emoji": "🤖",
        }

# ---------- Build full month list ----------
all_months = []
for y in range(2020, 2027):
    for m in range(1, 13):
        if y == 2026 and m > 6:
            break
        all_months.append(f"{y}-{m:02d}")

# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "mode" not in st.session_state:
    st.session_state.mode = "🕰️ Time Travel"

# ---------- Mode toggle ----------
mode = st.radio(
    "Choose your mode:",
    ["🕰️ Time Travel", "🌍 Free Ask"],
    horizontal=True,
    key="mode_toggle",
)

# ---------- Pick theme based on mode ----------
if mode == "🕰️ Time Travel":
    month = st.selectbox("🌀 Travel to:", options=all_months, index=all_months.index("2020-03"))
    year = int(month[:4])
    theme = get_theme(year)
else:
    theme = {
        "bg": "linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)",
        "accent": "#e94560",
        "era": "🌍 Free Ask — searching all years",
        "emoji": "🌍",
    }

# ---------- Dynamic CSS ----------
st.markdown(f"""
<style>
.stApp {{
    background: {theme['bg']};
}}
h1 {{
    font-family: 'Georgia', serif;
    text-align: center;
    color: #f5f5f5 !important;
    text-shadow: 0 0 20px {theme['accent']}99;
    margin-bottom: 0;
}}
.subtitle {{
    text-align: center;
    color: #cccccc;
    font-style: italic;
    margin-top: 4px;
    margin-bottom: 6px;
}}
.era-badge {{
    text-align: center;
    background: rgba(0,0,0,0.25);
    color: {theme['accent']};
    font-weight: bold;
    font-size: 0.9rem;
    letter-spacing: 1px;
    border-radius: 20px;
    padding: 6px 0;
    margin-bottom: 1.2rem;
}}
.ticker {{
    background: rgba(0,0,0,0.3);
    border-left: 4px solid {theme['accent']};
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 1.2rem;
    color: #eaeaea;
    font-size: 0.88rem;
    line-height: 1.7;
}}
.capsule-card {{
    background: rgba(255,255,255,0.06);
    border: 1px solid {theme['accent']}55;
    border-radius: 16px;
    padding: 22px;
    margin-top: 14px;
}}
.capsule-label {{
    color: {theme['accent']};
    font-weight: bold;
    font-size: 0.8rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}
.no-data-card {{
    background: rgba(255,165,0,0.08);
    border: 1px solid orange;
    border-radius: 16px;
    padding: 22px;
    margin-top: 14px;
}}
div[data-testid="stTextInput"] input {{
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 10px !important;
}}
div.stButton > button {{
    background: {theme['accent']};
    color: black;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
}}
div.stButton > button:hover {{
    opacity: 0.85;
}}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("<h1>🕰️ AI Time Capsule & Trend Oracle</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Step into any month from the past — the AI only knows what existed then.</p>', unsafe_allow_html=True)
st.markdown(f'<div class="era-badge">{theme["era"]}</div>', unsafe_allow_html=True)

# ---------- Live ticker (Time Travel mode only) ----------
@st.cache_data(show_spinner=False)
def get_snapshot(month_prefix):
    news = search("major news headline", month_prefix, top_k=1)
    song = search("popular song music", month_prefix, top_k=1)
    return news, song

if mode == "🕰️ Time Travel":
    news_hits, song_hits = get_snapshot(month)
    ticker_lines = []
    if news_hits:
        ticker_lines.append(f"📰 <b>News:</b> {news_hits[0]['text'][:100]}...")
    if song_hits:
        ticker_lines.append(f"🎵 <b>Music:</b> {song_hits[0]['text'][:100]}...")
    if ticker_lines:
        st.markdown(f'<div class="ticker">{"<br>".join(ticker_lines)}</div>', unsafe_allow_html=True)

# ---------- Input ----------
if mode == "🕰️ Time Travel":
    placeholder = "What was everyone talking about? What song was #1?"
else:
    placeholder = "When did COVID lockdowns start? Who won the 2020 US election?"

question = st.text_input("💭 Ask the time capsule:", placeholder=placeholder)

col1, col2 = st.columns([1, 1])
with col1:
    ask_clicked = st.button("✨ Ask", use_container_width=True)
with col2:
    if st.button("🗑️ Clear history", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ---------- On ask ----------
if ask_clicked and question:
    if mode == "🕰️ Time Travel":
        with st.spinner(f"📡 Tuning into {month}..."):
            result, sources, has_data = answer(question, month)
        label = month
    else:
        with st.spinner("🔍 Searching across all years (2015–2026)..."):
            result, sources, has_data = answer_free(question)
        label = "All years"

    st.session_state.history.insert(0, {
        "label": label,
        "question": question,
        "answer": result,
        "sources": sources,
        "has_data": has_data,
    })

# ---------- Display history ----------
for entry in st.session_state.history:
    if entry["has_data"]:
        st.markdown(f"""
        <div class="capsule-card">
            <div class="capsule-label">📍 {entry['label']}</div>
            <p style="color:#f5f5f5; margin-top:8px;"><b>You asked:</b> {entry['question']}</p>
            <p style="color:#e0e0e0; line-height:1.7;">{entry['answer']}</p>
        </div>
        """, unsafe_allow_html=True)

        if entry.get("sources"):
            with st.expander("🔍 Sources the AI used"):
                for s in entry["sources"]:
                    st.caption(f"[{s['date']} | {s['source']}] {s['text'][:150]}...")
    else:
        st.markdown(f"""
        <div class="no-data-card">
            <div style="color:orange; font-weight:bold; font-size:0.8rem;
                        letter-spacing:1.5px; text-transform:uppercase;">⚠️ Limited Data</div>
            <p style="color:#f5f5f5; margin-top:8px;"><b>You asked:</b> {entry['question']}</p>
            <p style="color:#e0e0e0; line-height:1.7;">{entry['answer']}</p>
        </div>
        """, unsafe_allow_html=True)


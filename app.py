import streamlit as st
import json
import os
import time
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()
FEEDBACK_FILE = "data/feedback.json"
HISTORY_FILE  = "data/history.json"
MODEL         = "llama-3.3-70b-versatile"

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NexusAI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

  /* ── Root palette ── */
  :root {
    --bg-primary:   #0d0f14;
    --bg-card:      #13161e;
    --bg-hover:     #1a1e2a;
    --accent:       #6c63ff;
    --accent-light: #a89cff;
    --accent-glow:  rgba(108,99,255,0.25);
    --green:        #00e5a0;
    --amber:        #ffb547;
    --red:          #ff5f6d;
    --text-primary: #eef0f6;
    --text-muted:   #7a80a0;
    --border:       rgba(108,99,255,0.18);
  }

  /* ── Global reset ── */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0f14 0%, #11141d 100%) !important;
    border-right: 1px solid var(--border) !important;
  }
  section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

  /* ── Header ── */
  .nexus-header {
    background: linear-gradient(135deg, #13161e 0%, #1a1040 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .nexus-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
    pointer-events: none;
  }
  .nexus-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #fff 30%, var(--accent-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
  }
  .nexus-header p {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin: 0;
  }

  /* ── Mode pill tabs ── */
  .mode-bar {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 24px;
  }
  .mode-pill {
    padding: 8px 20px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-muted);
    transition: all 0.2s;
  }
  .mode-pill.active {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
    box-shadow: 0 0 18px var(--accent-glow);
  }

  /* ── Cards ── */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 18px;
    transition: border-color 0.2s;
  }
  .card:hover { border-color: var(--accent); }

  /* ── Output box ── */
  .output-box {
    background: linear-gradient(135deg, #13161e, #111428);
    border: 1px solid var(--accent);
    border-radius: 12px;
    padding: 22px 26px;
    margin-top: 16px;
    line-height: 1.75;
    font-size: 0.97rem;
    box-shadow: 0 0 24px var(--accent-glow);
    white-space: pre-wrap;
  }

  /* ── Stat chips ── */
  .stat-row { display:flex; gap:12px; flex-wrap:wrap; margin-top:12px; }
  .stat-chip {
    background: rgba(108,99,255,0.1);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: var(--accent-light);
  }

  /* ── Feedback item ── */
  .fb-item {
    background: var(--bg-card);
    border-left: 3px solid var(--accent);
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 0.9rem;
  }
  .fb-meta { color: var(--text-muted); font-size: 0.78rem; margin-top: 6px; }

  /* ── History item ── */
  .hist-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.88rem;
  }
  .hist-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-bottom: 6px;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, var(--accent), #9b59f5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 4px 14px var(--accent-glow) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px var(--accent-glow) !important;
  }

  /* ── Inputs & textareas ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
  }

  /* ── Slider ── */
  .stSlider > div { color: var(--accent-light) !important; }

  /* ── Spinner hide default ── */
  div[data-testid="stSpinner"] > div { border-top-color: var(--accent) !important; }

  /* ── Metrics ── */
  [data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    color: var(--accent-light) !important;
  }
  [data-testid="stMetricLabel"] { color: var(--text-muted) !important; }

  /* ── Dividers ── */
  hr { border-color: var(--border) !important; }

  /* ── Radio ── */
  .stRadio label { color: var(--text-primary) !important; }

  /* ── Toast-like success ── */
  .success-chip {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(0,229,160,0.12);
    border:1px solid var(--green);
    color:var(--green);
    border-radius:8px;
    padding:6px 14px;
    font-size:0.83rem;
    font-weight:500;
    margin-top:10px;
  }
</style>
""", unsafe_allow_html=True)


# ── Helpers: data persistence ─────────────────────────────────────────────────
def load_json(path: str) -> list:
    os.makedirs("data", exist_ok=True)
    if os.path.exists(path):
        try:
            return json.load(open(path))
        except Exception:
            return []
    return []

def save_json(path: str, data: list) -> None:
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def append_json(path: str, entry: dict) -> None:
    data = load_json(path)
    data.append(entry)
    save_json(path, data)


# ── Groq client ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.getenv("GROQ_API_KEY") or st.session_state.get("api_key", "")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def call_groq(prompt: str, system: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
    client = get_client()
    if client is None:
        return "⚠️ No API key set. Add GROQ_API_KEY to your .env or enter it in the sidebar."
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system",  "content": system},
                {"role": "user",    "content": prompt},
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API Error: {e}"


# ── System prompts ─────────────────────────────────────────────────────────────
SYSTEM_QA = """You are a precise, knowledgeable assistant. Answer questions clearly and accurately.
Structure your answers with brief context, the main answer, and (when relevant) examples.
Keep it concise but complete."""

SYSTEM_SUMMARIZE = """You are an expert summarizer. Extract the key ideas from the given text.
Format: start with a 1-sentence TL;DR, then bullet points of key points, then a brief conclusion.
Match the summary length to what was requested."""

SYSTEM_CREATIVE = """You are a brilliant creative writer. Produce vivid, original, engaging content.
Avoid clichés. Match the requested tone and format exactly. Be bold with imagery and voice."""

SYSTEM_FEEDBACK_REPLY = """You are a helpful assistant acknowledging user feedback warmly and professionally."""


# ── Session state defaults ────────────────────────────────────────────────────
for key, default in {
    "mode": "Question Answering",
    "last_output": "",
    "last_input": "",
    "total_queries": 0,
    "api_key": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🧠 NexusAI")
    st.markdown("---")

    # API key input
    api_input = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="gsk_xxxxxxxxxxxx",
        help="Get a free key at console.groq.com",
    )
    if api_input != st.session_state.api_key:
        st.session_state.api_key = api_input
        os.environ["GROQ_API_KEY"] = api_input
        st.cache_resource.clear()

    st.markdown("---")

    # Mode selector
    st.markdown("**Select Mode**")
    modes = {
        "🔍 Question Answering":  "Question Answering",
        "📄 Text Summarization":  "Text Summarization",
        "✍️ Creative Writing":    "Creative Writing",
        "💬 Feedback":            "Feedback",
        "📊 Dashboard":           "Dashboard",
    }
    for label, value in modes.items():
        if st.button(label, use_container_width=True, key=f"btn_{value}"):
            st.session_state.mode = value

    st.markdown("---")

    # Settings
    st.markdown("**Settings**")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7, 0.05,
                            help="Higher = more creative; lower = more factual")
    max_tokens  = st.slider("Max Response Length", 256, 2048, 1024, 128)

    st.markdown("---")
    st.markdown(
        "<div style='color:#7a80a0;font-size:0.78rem;'>"
        "Powered by <b>Groq LLaMA-3 70B</b><br>"
        "Built with Streamlit · 2024"
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="nexus-header">
  <h1>🧠 NexusAI Assistant</h1>
  <p>Your intelligent companion for answers, summaries, creative writing, and more.</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MODE: QUESTION ANSWERING
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == "Question Answering":
    st.markdown("## 🔍 Question Answering")
    st.markdown("Ask anything — factual, conceptual, technical, or analytical.")

    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_area(
            "Your Question",
            height=110,
            placeholder="e.g. What is the difference between supervised and unsupervised learning?",
            key="qa_input",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        detail_level = st.selectbox("Detail Level", ["Concise", "Standard", "In-depth"], index=1)
        domain       = st.selectbox("Domain", ["General", "Tech / CS", "Science", "Business", "History"])

    if st.button("Get Answer →", key="qa_btn"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            prompt = (
                f"Domain: {domain}\n"
                f"Detail level: {detail_level}\n\n"
                f"Question: {question}"
            )
            with st.spinner("Thinking…"):
                t0     = time.time()
                answer = call_groq(prompt, SYSTEM_QA, temperature, max_tokens)
                elapsed = round(time.time() - t0, 2)

            st.markdown(f'<div class="output-box">{answer}</div>', unsafe_allow_html=True)

            word_count = len(answer.split())
            st.markdown(
                f'<div class="stat-row">'
                f'<span class="stat-chip">⏱ {elapsed}s</span>'
                f'<span class="stat-chip">📝 {word_count} words</span>'
                f'<span class="stat-chip">🔧 {domain}</span>'
                f'<span class="stat-chip">📊 {detail_level}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Save to history
            st.session_state.total_queries += 1
            append_json(HISTORY_FILE, {
                "mode": "QA", "input": question, "output": answer,
                "domain": domain, "timestamp": datetime.now().isoformat(),
            })
            st.session_state.last_output = answer
            st.session_state.last_input  = question


# ═══════════════════════════════════════════════════════════════════════════════
# MODE: TEXT SUMMARIZATION
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "Text Summarization":
    st.markdown("## 📄 Text Summarization")
    st.markdown("Paste any text — article, report, notes — and get a structured summary.")

    text_input = st.text_area(
        "Text to Summarize",
        height=220,
        placeholder="Paste your article, research paper, report, or any long text here…",
        key="sum_input",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        summary_style = st.selectbox("Style", ["Bullet Points", "Paragraph", "Executive Brief"])
    with col2:
        summary_len   = st.selectbox("Length", ["Short (3-5 pts)", "Medium (5-8 pts)", "Detailed (8-12 pts)"])
    with col3:
        language      = st.selectbox("Language", ["English", "Hinglish", "Simple English"])

    if st.button("Summarize →", key="sum_btn"):
        if not text_input.strip():
            st.warning("Please paste some text to summarize.")
        elif len(text_input.split()) < 30:
            st.warning("Text is too short to summarize. Please paste at least a paragraph.")
        else:
            prompt = (
                f"Style: {summary_style}\nLength: {summary_len}\nLanguage: {language}\n\n"
                f"Text:\n{text_input}"
            )
            with st.spinner("Summarizing…"):
                t0      = time.time()
                summary = call_groq(prompt, SYSTEM_SUMMARIZE, temperature, max_tokens)
                elapsed = round(time.time() - t0, 2)

            st.markdown(f'<div class="output-box">{summary}</div>', unsafe_allow_html=True)

            original_words = len(text_input.split())
            summary_words  = len(summary.split())
            reduction      = round((1 - summary_words / max(original_words, 1)) * 100)

            st.markdown(
                f'<div class="stat-row">'
                f'<span class="stat-chip">⏱ {elapsed}s</span>'
                f'<span class="stat-chip">📥 {original_words} → {summary_words} words</span>'
                f'<span class="stat-chip">📉 {reduction}% reduction</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.session_state.total_queries += 1
            append_json(HISTORY_FILE, {
                "mode": "Summarize", "input": text_input[:200] + "…",
                "output": summary, "style": summary_style,
                "timestamp": datetime.now().isoformat(),
            })
            st.session_state.last_output = summary


# ═══════════════════════════════════════════════════════════════════════════════
# MODE: CREATIVE WRITING
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "Creative Writing":
    st.markdown("## ✍️ Creative Writing")
    st.markdown("Generate original content — stories, poems, emails, ads, scripts, and more.")

    col1, col2 = st.columns([1, 1])
    with col1:
        content_type = st.selectbox("Content Type", [
            "Short Story", "Poem", "Professional Email", "Product Description",
            "Blog Introduction", "Dialogue / Script", "Motivational Speech",
            "Social Media Post", "Cover Letter", "Rap / Song Lyrics",
        ])
    with col2:
        tone = st.selectbox("Tone", [
            "Professional", "Casual & Friendly", "Humorous", "Dramatic",
            "Inspirational", "Academic", "Romantic", "Mysterious",
        ])

    prompt_input = st.text_area(
        "Your Prompt / Topic",
        height=130,
        placeholder="e.g. A story about an AI that becomes self-aware during a hackathon…",
        key="cw_input",
    )

    col3, col4 = st.columns(2)
    with col3:
        target_words = st.selectbox("Target Length", ["~100 words", "~250 words", "~500 words", "~800 words"])
    with col4:
        audience = st.selectbox("Target Audience", ["General", "Students", "Professionals", "Children", "Tech Enthusiasts"])

    if st.button("Generate →", key="cw_btn"):
        if not prompt_input.strip():
            st.warning("Please enter a topic or prompt.")
        else:
            full_prompt = (
                f"Content type: {content_type}\n"
                f"Tone: {tone}\n"
                f"Target audience: {audience}\n"
                f"Approximate length: {target_words}\n\n"
                f"Prompt: {prompt_input}"
            )
            with st.spinner("Creating…"):
                t0      = time.time()
                content = call_groq(full_prompt, SYSTEM_CREATIVE, min(temperature + 0.1, 1.0), max_tokens)
                elapsed = round(time.time() - t0, 2)

            st.markdown(f'<div class="output-box">{content}</div>', unsafe_allow_html=True)

            word_count = len(content.split())
            st.markdown(
                f'<div class="stat-row">'
                f'<span class="stat-chip">⏱ {elapsed}s</span>'
                f'<span class="stat-chip">✍️ {word_count} words</span>'
                f'<span class="stat-chip">🎭 {tone}</span>'
                f'<span class="stat-chip">📑 {content_type}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.session_state.total_queries += 1
            append_json(HISTORY_FILE, {
                "mode": "Creative", "input": prompt_input, "output": content,
                "content_type": content_type, "tone": tone,
                "timestamp": datetime.now().isoformat(),
            })
            st.session_state.last_output = content

    # Download last output
    if st.session_state.last_output and st.session_state.mode == "Creative Writing":
        st.download_button(
            "⬇ Download Output",
            data=st.session_state.last_output,
            file_name=f"nexusai_creative_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MODE: FEEDBACK
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "Feedback":
    st.markdown("## 💬 Feedback & Ratings")
    st.markdown("Share your experience and help improve NexusAI.")

    with st.form("feedback_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("Your Name (optional)", placeholder="e.g. Harsh")
        with col2:
            feature_used = st.selectbox(
                "Which feature did you use?",
                ["Question Answering", "Text Summarization", "Creative Writing", "General / All"],
            )

        rating = st.radio(
            "Overall Rating",
            ["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"],
            horizontal=True,
            index=4,
        )

        feedback_text = st.text_area(
            "Your Feedback",
            height=120,
            placeholder="What did you like? What could be improved? Any bugs?",
        )

        use_case = st.text_input(
            "How are you using NexusAI?",
            placeholder="e.g. College assignment, research, daily productivity…",
        )

        submitted = st.form_submit_button("Submit Feedback →")

        if submitted:
            if not feedback_text.strip():
                st.warning("Please write some feedback before submitting.")
            else:
                entry = {
                    "name":         user_name or "Anonymous",
                    "feature":      feature_used,
                    "rating":       rating,
                    "feedback":     feedback_text,
                    "use_case":     use_case,
                    "timestamp":    datetime.now().isoformat(),
                }
                append_json(FEEDBACK_FILE, entry)

                # AI acknowledgement
                ack = call_groq(
                    f"User rated us: {rating}. Feedback: {feedback_text[:200]}. "
                    "Write a warm 1-sentence thank-you acknowledgement.",
                    SYSTEM_FEEDBACK_REPLY, 0.5, 80,
                )
                st.markdown(
                    f'<div class="success-chip">✅ Feedback saved!</div>',
                    unsafe_allow_html=True,
                )
                st.info(f"🤖 {ack}")

    st.markdown("---")
    st.markdown("### Recent Feedback")
    feedbacks = load_json(FEEDBACK_FILE)
    if feedbacks:
        for fb in reversed(feedbacks[-8:]):
            ts   = fb.get("timestamp", "")[:10]
            name = fb.get("name", "Anonymous")
            st.markdown(
                f'<div class="fb-item">'
                f'<b>{fb["rating"]}</b> — <i>{fb["feedback"]}</i>'
                f'<div class="fb-meta">{name} · {fb["feature"]} · {ts}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No feedback yet. Be the first!")


# ═══════════════════════════════════════════════════════════════════════════════
# MODE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "Dashboard":
    st.markdown("## 📊 Usage Dashboard")

    history  = load_json(HISTORY_FILE)
    feedback = load_json(FEEDBACK_FILE)

    total    = len(history)
    qa_count = sum(1 for h in history if h.get("mode") == "QA")
    sm_count = sum(1 for h in history if h.get("mode") == "Summarize")
    cw_count = sum(1 for h in history if h.get("mode") == "Creative")
    fb_count = len(feedback)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Queries",       total)
    c2.metric("Q&A Sessions",        qa_count)
    c3.metric("Summaries Created",   sm_count)
    c4.metric("Creative Pieces",     cw_count)

    st.markdown("---")
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.markdown("### Recent Activity")
        if history:
            for h in reversed(history[-10:]):
                mode_colors = {
                    "QA": "#6c63ff", "Summarize": "#00e5a0", "Creative": "#ffb547"
                }
                badge_color = mode_colors.get(h.get("mode", ""), "#7a80a0")
                mode_label  = {"QA": "Q&A", "Summarize": "Summary", "Creative": "Creative"}.get(h.get("mode", ""), h.get("mode", ""))
                ts          = h.get("timestamp", "")[:16].replace("T", " ")
                inp         = h.get("input", "")[:80]
                out_preview = h.get("output", "")[:100]
                st.markdown(
                    f'<div class="hist-item">'
                    f'<span class="hist-badge" style="background:{badge_color}20;color:{badge_color};border:1px solid {badge_color}40">'
                    f'{mode_label}</span><br>'
                    f'<b>→</b> {inp}…<br>'
                    f'<span style="color:#7a80a0;font-size:0.82rem">{out_preview}…</span>'
                    f'<div class="fb-meta">{ts}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No queries yet. Start using the assistant!")

    with col_r:
        st.markdown("### Feedback Stats")
        if feedback:
            five_star = sum(1 for f in feedback if "⭐⭐⭐⭐⭐" in f.get("rating", ""))
            four_star = sum(1 for f in feedback if f.get("rating","").count("⭐") == 4)
            st.markdown(
                f'<div class="card">'
                f'<div style="font-size:2rem;font-weight:700;color:#6c63ff">{fb_count}</div>'
                f'<div style="color:#7a80a0">Total Reviews</div>'
                f'<div class="stat-row" style="margin-top:12px">'
                f'<span class="stat-chip">⭐⭐⭐⭐⭐ {five_star}</span>'
                f'<span class="stat-chip">⭐⭐⭐⭐ {four_star}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            st.markdown("**Recent Reviews**")
            for fb in reversed(feedback[-4:]):
                st.markdown(
                    f'<div class="fb-item" style="font-size:0.82rem">'
                    f'{fb["rating"]}<br><i>"{fb["feedback"][:80]}…"</i>'
                    f'<div class="fb-meta">{fb["name"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No feedback yet.")

    st.markdown("---")
    col_dl1, col_dl2, _ = st.columns([1, 1, 2])
    with col_dl1:
        if history:
            st.download_button(
                "⬇ Export History (JSON)",
                data=json.dumps(history, indent=2),
                file_name="nexusai_history.json",
                mime="application/json",
            )
    with col_dl2:
        if feedback:
            st.download_button(
                "⬇ Export Feedback (JSON)",
                data=json.dumps(feedback, indent=2),
                file_name="nexusai_feedback.json",
                mime="application/json",
            )

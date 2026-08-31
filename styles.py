"""
Custom CSS injected into the Streamlit app.

Design concept: the resume is a paper document; the ATS is a machine
reading it. Serif type (Fraunces) carries the "paper/human" side of the
page - headers, hero, section titles. Monospace type (IBM Plex Mono)
carries the "machine/data" side - scores, keyword pills, metrics - as if
a scanner printed them out. Matched keywords are styled like a highlighter
stripe; missing ones like a red stamp mark.
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600;700&display=swap');

    :root {
        --paper: #F6F3EA;
        --paper-card: #FFFDF8;
        --ink: #1E2A38;
        --ink-soft: #6B6558;
        --line: #E4DFD0;
        --signal: #24487A;
        --signal-2: #3E6FA8;
        --highlight-bg: #ECEE9C;
        --highlight-line: #C7CC5E;
        --flag-bg: #F7E4DE;
        --flag-text: #9B3226;
        --flag-line: #E8B9AC;
        --amber: #B5792A;
        --green: #2F6E4F;
        --font-display: 'Fraunces', Georgia, serif;
        --font-body: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'IBM Plex Mono', 'Courier New', monospace;
    }

    html {
        scroll-behavior: smooth;
    }
    #home, #analyse-section, #how-it-works {
        scroll-margin-top: 1.2rem;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}

    .stApp {
        background: var(--paper);
        color: var(--ink);
        font-family: var(--font-body);
    }
    html, body, [class*="css"] { font-family: var(--font-body); }

    .block-container {
        padding-top: 1.5rem;
        max-width: 1080px;
    }

    h1, h2, h3, h4 { font-family: var(--font-display); color: var(--ink); }

    /* ---------- Navbar ---------- */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--paper-card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.9rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 2px rgba(30, 42, 56, 0.05);
    }
    .navbar-logo {
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 1.2rem;
        color: var(--ink);
    }
    .navbar-links {
        display: flex;
        gap: 1.5rem;
        color: var(--ink-soft);
        font-weight: 600;
        font-size: 0.9rem;
    }
    .navbar-links a {
        color: var(--ink-soft);
        text-decoration: none;
        transition: color 0.15s ease;
    }
    .navbar-links a:hover {
        color: var(--signal);
    }
    .navbar-badge {
        background: var(--signal);
        color: var(--paper-card);
        font-family: var(--font-mono);
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
    }

    /* ---------- Hero ---------- */
    .hero {
        text-align: center;
        padding: 2.6rem 1rem 2rem 1rem;
    }
    .hero-badge {
        display: inline-block;
        font-family: var(--font-mono);
        color: var(--signal);
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
    }
    .hero h1 {
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0 0 0.7rem 0;
        color: var(--ink);
    }
    .hero p {
        color: var(--ink-soft);
        font-size: 1.05rem;
        max-width: 600px;
        margin: 0 auto;
    }

    /* ---------- Step progress ---------- */
    .steps {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--paper-card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.1rem 1.8rem;
        margin: 1.5rem 0;
    }
    .step {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        color: var(--ink-soft);
        font-weight: 600;
        font-size: 0.88rem;
        white-space: nowrap;
    }
    .step-dot {
        width: 26px;
        height: 26px;
        min-width: 26px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 700;
        border: 2px solid var(--line);
        color: var(--ink-soft);
        background: var(--paper);
    }
    .step.done { color: var(--ink); }
    .step.done .step-dot { background: var(--signal); border-color: var(--signal); color: var(--paper-card); }
    .step.active { color: var(--ink); }
    .step.active .step-dot {
        background: var(--paper-card); border-color: var(--signal); color: var(--signal);
        box-shadow: 0 0 0 4px rgba(36, 72, 122, 0.14);
        animation: pulse-ring 2s ease-in-out infinite;
    }
    @keyframes pulse-ring {
        0%, 100% { box-shadow: 0 0 0 4px rgba(36, 72, 122, 0.14); }
        50% { box-shadow: 0 0 0 7px rgba(36, 72, 122, 0.08); }
    }
    .step-line { flex: 1; height: 2px; background: var(--line); margin: 0 0.7rem; min-width: 16px; }
    .step-line.done { background: var(--signal); }

    /* ---------- Generic Card ---------- */
    .card {
        background: var(--paper-card);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 2px rgba(30, 42, 56, 0.05);
    }
    .card h3, .card h4 {
        margin-top: 0;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .eyebrow {
        font-family: var(--font-mono);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--ink-soft);
        margin-bottom: 0.5rem;
    }

    /* ---------- Empty state ---------- */
    .empty-state {
        text-align: center;
        padding: 2rem 1rem;
        color: var(--ink-soft);
    }
    .feature-mini {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: var(--paper);
        border: 1px solid var(--line);
        color: var(--ink);
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.3rem;
    }

    /* ---------- Verdict / score seal ---------- */
    .verdict-wrap { display: flex; gap: 1.8rem; align-items: center; flex-wrap: wrap; }
    .stamp-outer {
        width: 148px; height: 148px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
    }
    .stamp {
        width: 118px; height: 118px; border-radius: 50%;
        border: 2px solid var(--stamp-color, var(--signal));
        box-shadow: 0 0 0 4px var(--paper-card), 0 0 0 5.5px var(--stamp-color, var(--signal));
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        background: var(--paper-card);
    }
    .stamp .val {
        font-family: var(--font-mono); font-size: 2rem; font-weight: 700;
        color: var(--stamp-color, var(--signal)); line-height: 1;
    }
    .stamp .lbl {
        font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase;
        color: var(--ink-soft); margin-top: 4px; font-weight: 600;
    }
    .verdict-summary { flex: 1; min-width: 260px; }
    .verdict-summary p { margin: 0; color: var(--ink); line-height: 1.55; }

    /* ---------- Metric cards ---------- */
    .metric-card {
        background: var(--paper-card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.1rem;
        text-align: center;
    }
    .metric-card .label {
        font-family: var(--font-mono);
        color: var(--ink-soft);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .metric-card .value {
        font-family: var(--font-mono);
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--ink);
    }
    .metric-bar-track {
        width: 100%;
        height: 5px;
        border-radius: 999px;
        background: var(--line);
        margin-top: 0.55rem;
        overflow: hidden;
    }
    .metric-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: var(--signal);
    }

    /* ---------- Pills ---------- */
    .pill {
        display: inline-block;
        font-family: var(--font-mono);
        border-radius: 6px;
        padding: 0.32rem 0.8rem;
        margin: 0.22rem;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .pill-good {
        background: var(--highlight-bg);
        color: var(--ink);
        border: 1px solid var(--highlight-line);
    }
    .pill-bad {
        background: var(--flag-bg);
        color: var(--flag-text);
        border: 1px solid var(--flag-line);
    }

    /* ---------- History (in-session) ---------- */
    .history-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0.2rem;
        border-bottom: 1px dashed var(--line);
        font-size: 0.9rem;
    }
    .history-item:last-child { border-bottom: none; }
    .history-jd { color: var(--ink); font-weight: 500; }
    .history-score {
        font-family: var(--font-mono);
        font-weight: 700;
        font-size: 0.82rem;
        padding: 0.15rem 0.7rem;
        border-radius: 6px;
    }

    /* ---------- Footer ---------- */
    .app-footer {
        text-align: center;
        color: var(--ink-soft);
        padding: 2rem 0 1rem 0;
        font-size: 0.85rem;
        border-top: 1px solid var(--line);
        margin-top: 2rem;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 700;
        padding: 0.6rem 1.4rem;
        border: 1px solid var(--signal);
        background: var(--signal);
        color: var(--paper-card);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(36, 72, 122, 0.22);
        background: var(--signal-2);
        color: var(--paper-card);
        border-color: var(--signal-2);
    }

    div.stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700;
        background: var(--green);
        color: var(--paper-card);
        border: 1px solid var(--green);
    }
    div.stDownloadButton > button:hover {
        background: #255c40;
        color: var(--paper-card);
    }

    /* File uploader dropzone */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
        border: 1.5px dashed var(--line);
        background: var(--paper);
    }

    /* ---------- Textarea (fixed: force light theme regardless of
       system/browser dark mode, so typed text stays visible) ---------- */
    textarea {
        border-radius: 10px !important;
        font-family: var(--font-body) !important;
        background: var(--paper-card) !important;
        color: var(--ink) !important;
        caret-color: var(--ink) !important;
    }
    textarea::placeholder {
        color: var(--ink-soft) !important;
        opacity: 1 !important;
    }
    [data-testid="stTextArea"] {
        background: var(--paper-card) !important;
    }

    /* ---------- Mobile responsiveness ---------- */
    html, body {
        overflow-x: hidden;
    }

    @media (max-width: 640px) {
        .navbar {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.8rem;
            padding: 1rem;
        }
        .navbar-links {
            flex-wrap: wrap;
            gap: 0.8rem 1.2rem;
            font-size: 0.85rem;
        }
        .navbar-badge {
            align-self: flex-start;
        }
        .hero h1 {
            font-size: 1.8rem;
        }
        .hero {
            padding: 1.6rem 0.5rem 1.4rem 0.5rem;
        }
        .steps {
            padding: 0.9rem;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .step {
            font-size: 0.78rem;
        }
        .verdict-wrap {
            flex-direction: column;
            text-align: center;
        }
    }
</style>
"""


def score_status_label(score: int) -> str:
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Strong"
    elif score >= 70:
        return "Good"
    return "Needs Work"


def score_status_color(score: int) -> str:
    if score >= 90:
        return "#2F6E4F"
    elif score >= 80:
        return "#24487A"
    elif score >= 70:
        return "#B5792A"
    return "#9B3226"


def render_score_ring(score: int) -> str:
    """Renders the score as a seal-style badge: an outer ring that fills
    proportionally to the score (so the score is visible as a proportion,
    not just a number), around an inner double-bordered seal with the
    number in monospace, like a stamped scan result."""
    color = score_status_color(score)
    label = score_status_label(score)
    return f"""
    <div class="stamp-outer" style="background: conic-gradient({color} calc({score} * 1%), var(--line) 0);">
        <div class="stamp" style="--stamp-color:{color};">
            <div class="val">{score}</div>
            <div class="lbl">{label}</div>
        </div>
    </div>
    """


def render_metric_card(label: str, value: int) -> str:
    return f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value">{value}%</div>
        <div class="metric-bar-track">
            <div class="metric-bar-fill" style="width:{value}%;"></div>
        </div>
    </div>
    """


def render_pills(items: list, kind: str = "good") -> str:
    if not items:
        return "<i>None</i>"
    css_class = "pill-good" if kind == "good" else "pill-bad"
    return "".join(f'<span class="pill {css_class}">{item}</span>' for item in items)


def render_step_progress(current_step: int) -> str:
    """current_step: 1=Upload, 2=Analyze, 3=Optimize, 4=Download.
    Steps before current_step are marked done; the current one is active."""
    labels = ["Upload", "Analyze", "Optimize", "Download"]
    parts = []
    for i, label in enumerate(labels, start=1):
        if i < current_step:
            state = "done"
            dot = "&#10003;"
        elif i == current_step:
            state = "active"
            dot = str(i)
        else:
            state = ""
            dot = str(i)
        parts.append(f'<div class="step {state}"><div class="step-dot">{dot}</div>{label}</div>')
        if i < len(labels):
            line_state = "done" if i < current_step else ""
            parts.append(f'<div class="step-line {line_state}"></div>')
    return f'<div class="steps">{"".join(parts)}</div>'


def render_history_item(jd_label: str, score: int) -> str:
    color = score_status_color(score)
    return f"""
    <div class="history-item">
        <span class="history-jd">{jd_label}</span>
        <span class="history-score" style="background:{color}1a; color:{color};">{score}%</span>
    </div>
    """
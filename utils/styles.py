"""
utils/styles.py
Custom CSS injection for DataMind AI – a dark-mode-first design using
a deep navy/teal palette with amber accents and IBM Plex Mono typography.
"""

import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;600;800&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── Root Palette ── */
    :root {
        --bg:        #0d1117;
        --surface:   #161b22;
        --border:    #21262d;
        --teal:      #3ddbd9;
        --amber:     #e6a817;
        --purple:    #a371f7;
        --text:      #e6edf3;
        --muted:     #8b949e;
        --danger:    #f85149;
        --success:   #3fb950;
        --radius:    10px;
        --font-head: 'Syne', sans-serif;
        --font-body: 'DM Sans', sans-serif;
        --font-mono: 'IBM Plex Mono', monospace;
    }

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: var(--font-body);
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .sidebar-header {
        display: flex; align-items: center; gap: 12px;
        padding: 1rem 0 .5rem;
    }
    .logo-mark {
        font-size: 2rem; color: var(--teal);
        animation: spin 8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .app-title {
        font-family: var(--font-head); font-size: 1.2rem;
        font-weight: 800; color: var(--text); letter-spacing: -.02em;
    }
    .app-sub { font-size: .75rem; color: var(--muted); }

    /* Radio nav styling */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 2px !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        font-family: var(--font-mono); font-size: .78rem;
        color: var(--muted); padding: 6px 10px;
        border-radius: 6px; transition: all .15s;
        cursor: pointer;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(61,219,217,.08); color: var(--teal);
    }

    .dataset-pill {
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(61,219,217,.06); border: 1px solid rgba(61,219,217,.15);
        border-radius: 6px; padding: 6px 12px; margin-bottom: 6px;
        font-family: var(--font-mono); font-size: .75rem; color: var(--muted);
    }
    .dataset-pill strong { color: var(--teal); }

    .sidebar-info { font-family: var(--font-mono); font-size: .7rem; }
    .info-label { color: var(--muted); letter-spacing: .1em; margin-bottom: 4px; }

    /* ── Page Titles ── */
    .page-title {
        font-family: var(--font-head) !important; font-size: 2rem !important;
        font-weight: 800 !important; color: var(--text) !important;
        letter-spacing: -.03em !important; margin-bottom: .25rem !important;
    }
    .page-sub { color: var(--muted); margin-bottom: 2rem; font-size: .95rem; }

    /* ── Metric Cards ── */
    [data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        font-family: var(--font-mono); font-size: .7rem;
        color: var(--muted); letter-spacing: .08em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: var(--font-head); font-size: 1.6rem;
        color: var(--teal);
    }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] { border-radius: var(--radius); overflow: hidden; }
    [data-testid="stDataFrame"] th {
        background: var(--surface) !important;
        font-family: var(--font-mono); font-size: .7rem;
        color: var(--muted); letter-spacing: .08em;
        border-bottom: 1px solid var(--border);
    }
    [data-testid="stDataFrame"] td {
        font-family: var(--font-mono); font-size: .78rem;
        color: var(--text);
    }

    /* ── Info Card ── */
    .info-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 1.25rem 1.5rem;
    }
    .ic-title {
        font-family: var(--font-mono); font-size: .65rem;
        color: var(--teal); letter-spacing: .12em; margin-bottom: .5rem;
    }
    .ic-item { font-size: .82rem; color: var(--muted); line-height: 1.8; }
    .ic-divider { border-top: 1px solid var(--border); margin: .75rem 0; }

    /* ── AI Box ── */
    .ai-box {
        background: linear-gradient(135deg, rgba(163,113,247,.07), rgba(61,219,217,.05));
        border: 1px solid rgba(163,113,247,.25);
        border-radius: var(--radius); padding: 1.5rem;
        font-size: .9rem; line-height: 1.75; color: var(--text);
        white-space: pre-wrap;
    }

    /* ── Insight Items ── */
    .insight-item {
        display: flex; gap: 12px; align-items: flex-start;
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
        font-size: .88rem; line-height: 1.6;
        transition: border-color .2s;
    }
    .insight-item:hover { border-color: var(--teal); }
    .ins-num {
        font-family: var(--font-mono); font-size: .65rem;
        color: var(--amber); opacity: .8; flex-shrink: 0; padding-top: 3px;
    }

    /* ── Buttons ── */
    [data-testid="stButton"] button {
        background: linear-gradient(135deg, var(--teal), #26a0a0) !important;
        color: #0d1117 !important; border: none !important;
        font-family: var(--font-mono) !important; font-size: .8rem !important;
        font-weight: 600 !important; letter-spacing: .05em !important;
        border-radius: 8px !important; padding: .6rem 1.2rem !important;
        transition: opacity .2s, transform .15s !important;
    }
    [data-testid="stButton"] button:hover {
        opacity: .9 !important; transform: translateY(-1px) !important;
    }

    /* ── Download Buttons ── */
    [data-testid="stDownloadButton"] button {
        background: transparent !important;
        border: 1px solid var(--teal) !important;
        color: var(--teal) !important;
        font-family: var(--font-mono) !important; font-size: .8rem !important;
        border-radius: 8px !important;
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        border: 1.5px dashed var(--border);
        border-radius: var(--radius); padding: 1.5rem;
        transition: border-color .2s;
    }
    [data-testid="stFileUploader"]:hover { border-color: var(--teal); }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius);
    }

    /* ── Alerts ── */
    [data-testid="stAlert"] {
        border-radius: var(--radius);
        font-family: var(--font-mono); font-size: .8rem;
    }

    /* ── Progress Bar ── */
    [data-testid="stProgress"] > div { background: var(--border) !important; }
    [data-testid="stProgress"] > div > div { background: var(--teal) !important; }

    /* ── Section Divider ── */
    .section-divider {
        border: none; border-top: 1px solid var(--border); margin: 2rem 0;
    }

    /* ── Tag Badge ── */
    .tag {
        display: inline-block;
        background: rgba(61,219,217,.12); color: var(--teal);
        border: 1px solid rgba(61,219,217,.2);
        border-radius: 4px; padding: 2px 8px;
        font-family: var(--font-mono); font-size: .7rem;
        margin: 2px;
    }
    .tag-amber {
        background: rgba(230,168,23,.12); color: var(--amber);
        border-color: rgba(230,168,23,.2);
    }
    .tag-danger {
        background: rgba(248,81,73,.12); color: var(--danger);
        border-color: rgba(248,81,73,.2);
    }
    .tag-success {
        background: rgba(63,185,80,.12); color: var(--success);
        border-color: rgba(63,185,80,.2);
    }

    /* ── Plotly overrides ── */
    .js-plotly-plot .plotly { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

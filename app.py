"""
AI Dataset Analyzer - "Explain Dataset Like a Professor"
Main Streamlit Application Entry Point
"""

import streamlit as st
import os
from pathlib import Path

# ─── Page Configuration ────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Dataset Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Import Utility Modules ─────────────────────────────────────────────────
from utils.data_loader    import load_dataset, display_dataset_overview
from utils.cleaning       import analyze_data_quality
from utils.statistics     import generate_statistics
from utils.visualizations import run_visualizations
from utils.ml_suggester   import suggest_ml_algorithms, detect_target_column
from utils.feature_importance import compute_feature_importance
from utils.ai_explainer   import generate_ai_explanation, generate_insights
from utils.pdf_report     import generate_pdf_report
from utils.styles         import inject_css

# ─── Inject Custom CSS ──────────────────────────────────────────────────────
inject_css()

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="logo-mark">⬡</div>
        <div>
            <div class="app-title">DataMind AI</div>
            <div class="app-sub">Dataset Analyzer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    nav = st.radio(
        "Navigation",
        [
            "📁  Upload Dataset",
            "🔍  Data Overview",
            "🧹  Data Quality",
            "📊  Statistics",
            "📈  Visualizations",
            "🤖  ML Suggestions",
            "⭐  Feature Importance",
            "🧠  AI Insights",
            "📄  PDF Report",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div class="sidebar-info">
        <div class="info-label">STATUS</div>
        <div id="status-text">No dataset loaded</div>
    </div>
    """, unsafe_allow_html=True)

    # Show dataset info if loaded
    if "df" in st.session_state and st.session_state.df is not None:
        df = st.session_state.df
        st.markdown(f"""
        <div class="dataset-pill">
            <span>Rows</span><strong>{df.shape[0]:,}</strong>
        </div>
        <div class="dataset-pill">
            <span>Cols</span><strong>{df.shape[1]}</strong>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("© 2025 DataMind AI · Built with Streamlit")

# ─── Main Content ────────────────────────────────────────────────────────────
section = nav.split("  ", 1)[1].strip()

# ──────────────────────────────────────────────────────────────────
# SECTION 1: Upload Dataset
# ──────────────────────────────────────────────────────────────────
if section == "Upload Dataset":
    st.markdown('<h1 class="page-title">Upload Your Dataset</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Drop a CSV file to begin AI-powered analysis</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            help="Upload any CSV dataset for full AI-powered analysis",
        )

        if uploaded_file:
            with st.spinner("Loading dataset…"):
                df, msg = load_dataset(uploaded_file)
            if df is not None:
                st.session_state.df       = df
                st.session_state.filename = uploaded_file.name
                st.success(f"✅ {msg}")
                st.markdown("### Preview (first 5 rows)")
                st.dataframe(df.head(), use_container_width=True)
                display_dataset_overview(df)
            else:
                st.error(msg)

    with col2:
        st.markdown("""
        <div class="info-card">
            <div class="ic-title">Supported Formats</div>
            <div class="ic-item">✓ UTF-8 CSV</div>
            <div class="ic-item">✓ Latin-1 CSV</div>
            <div class="ic-item">✓ Large files (100MB+)</div>
            <div class="ic-divider"></div>
            <div class="ic-title">Auto-Generated</div>
            <div class="ic-item">✓ Schema detection</div>
            <div class="ic-item">✓ Type inference</div>
            <div class="ic-item">✓ Quality scan</div>
            <div class="ic-item">✓ AI explanations</div>
        </div>
        """, unsafe_allow_html=True)

        # Sample dataset download
        sample_path = Path("assets/sample_dataset.csv")
        if sample_path.exists():
            with open(sample_path, "rb") as f:
                st.download_button(
                    "⬇ Download Sample CSV",
                    f,
                    file_name="sample_dataset.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

# ──────────────────────────────────────────────────────────────────
# Helper: guard for pages that require a loaded dataset
# ──────────────────────────────────────────────────────────────────
def require_dataset():
    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first from the **Upload Dataset** section.")
        st.stop()
    return st.session_state.df

# ──────────────────────────────────────────────────────────────────
# SECTION 2: Data Overview
# ──────────────────────────────────────────────────────────────────
elif section == "Data Overview":
    df = require_dataset()
    st.markdown('<h1 class="page-title">Data Overview</h1>', unsafe_allow_html=True)
    display_dataset_overview(df, detailed=True)

# ──────────────────────────────────────────────────────────────────
# SECTION 3: Data Quality
# ──────────────────────────────────────────────────────────────────
elif section == "Data Quality":
    df = require_dataset()
    st.markdown('<h1 class="page-title">Data Quality Analysis</h1>', unsafe_allow_html=True)
    analyze_data_quality(df)

# ──────────────────────────────────────────────────────────────────
# SECTION 4: Statistics
# ──────────────────────────────────────────────────────────────────
elif section == "Statistics":
    df = require_dataset()
    st.markdown('<h1 class="page-title">Statistical Summary</h1>', unsafe_allow_html=True)
    generate_statistics(df)

# ──────────────────────────────────────────────────────────────────
# SECTION 5: Visualizations
# ──────────────────────────────────────────────────────────────────
elif section == "Visualizations":
    df = require_dataset()
    st.markdown('<h1 class="page-title">Visualization Suite</h1>', unsafe_allow_html=True)
    run_visualizations(df)

# ──────────────────────────────────────────────────────────────────
# SECTION 6: ML Suggestions
# ──────────────────────────────────────────────────────────────────
elif section == "ML Suggestions":
    df = require_dataset()
    st.markdown('<h1 class="page-title">ML Algorithm Suggestions</h1>', unsafe_allow_html=True)
    target_col = detect_target_column(df)
    suggest_ml_algorithms(df, target_col)

# ──────────────────────────────────────────────────────────────────
# SECTION 7: Feature Importance
# ──────────────────────────────────────────────────────────────────
elif section == "Feature Importance":
    df = require_dataset()
    st.markdown('<h1 class="page-title">Feature Importance Analysis</h1>', unsafe_allow_html=True)
    compute_feature_importance(df)

# ──────────────────────────────────────────────────────────────────
# SECTION 8: AI Insights
# ──────────────────────────────────────────────────────────────────
elif section == "AI Insights":
    df = require_dataset()
    st.markdown('<h1 class="page-title">AI Professor Insights</h1>', unsafe_allow_html=True)

    api_key = st.text_input(
        "🔑 Enter your Google Gemini API Key (optional — basic insights work without it)",
        type="password",
        placeholder="AIza...",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Generate AI Explanation", use_container_width=True):
            with st.spinner("Professor is analyzing your dataset…"):
                explanation = generate_ai_explanation(df, api_key if api_key else None)
            st.markdown("### 📖 Professor's Analysis")
            st.markdown(f'<div class="ai-box">{explanation}</div>', unsafe_allow_html=True)

    with col2:
        if st.button("💡 Auto-Generate Insights", use_container_width=True):
            with st.spinner("Extracting hidden patterns…"):
                insights = generate_insights(df, api_key if api_key else None)
            st.markdown("### 🔍 Top Insights")
            for i, ins in enumerate(insights, 1):
                st.markdown(f'<div class="insight-item"><span class="ins-num">{i:02d}</span> {ins}</div>',
                            unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# SECTION 9: PDF Report
# ──────────────────────────────────────────────────────────────────
elif section == "PDF Report":
    df = require_dataset()
    st.markdown('<h1 class="page-title">PDF Report Generator</h1>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-bottom:1.5rem">
        The report includes: dataset summary · quality analysis · statistics ·
        chart thumbnails · AI insights · ML recommendations
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("🔑 Gemini API Key (optional)", type="password", placeholder="AIza…")

    if st.button("📄 Generate & Download PDF Report", use_container_width=True):
        with st.spinner("Building your professional report…"):
            progress = st.progress(0)
            pdf_bytes = generate_pdf_report(
                df,
                filename=st.session_state.get("filename", "dataset.csv"),
                api_key=api_key if api_key else None,
                progress_cb=lambda v: progress.progress(v),
            )
            progress.progress(100)

        st.success("✅ Report ready!")
        st.download_button(
            label="⬇ Download PDF Report",
            data=pdf_bytes,
            file_name="DataMind_AI_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

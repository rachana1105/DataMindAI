"""
utils/data_loader.py
Handles CSV ingestion, encoding detection, type inference, and overview display.
"""

import io
import streamlit as st
import pandas as pd
import numpy as np


# ─── Load Dataset ────────────────────────────────────────────────────────────

def load_dataset(uploaded_file) -> tuple[pd.DataFrame | None, str]:
    """
    Attempt to read an uploaded CSV file with multiple encoding fallbacks.
    Returns (DataFrame, success_message) or (None, error_message).
    """
    encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    raw = uploaded_file.read()

    for enc in encodings:
        try:
            df = pd.read_csv(io.BytesIO(raw), encoding=enc)
            # Basic sanity check
            if df.empty or df.shape[1] < 2:
                return None, "The uploaded file appears to be empty or has only one column."
            return df, f"Loaded **{uploaded_file.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns"
        except Exception:
            continue

    return None, "Could not parse the file. Ensure it is a valid UTF-8 or Latin-1 CSV."


# ─── Overview ────────────────────────────────────────────────────────────────

def display_dataset_overview(df: pd.DataFrame, detailed: bool = False):
    """Render key metrics and schema table for the dataset."""

    # Top-level KPI row
    num_cols   = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols   = df.select_dtypes(include=["object", "category"]).columns.tolist()
    miss_pct   = df.isnull().mean().mean() * 100
    dup_count  = df.duplicated().sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rows",         f"{df.shape[0]:,}")
    c2.metric("Columns",      f"{df.shape[1]}")
    c3.metric("Numeric Cols", f"{len(num_cols)}")
    c4.metric("Categorical",  f"{len(cat_cols)}")
    c5.metric("Missing %",    f"{miss_pct:.1f}%")

    if not detailed:
        return

    st.markdown("---")

    # Schema table
    schema = pd.DataFrame({
        "Column":       df.columns,
        "Type":         df.dtypes.astype(str).values,
        "Non-Null":     df.notnull().sum().values,
        "Null Count":   df.isnull().sum().values,
        "Null %":       (df.isnull().mean() * 100).round(2).astype(str).add("%").values,
        "Unique Values": df.nunique().values,
        "Sample":       [str(df[c].dropna().iloc[0]) if df[c].notnull().any() else "—" for c in df.columns],
    })

    st.markdown("#### Schema & Column Profile")
    st.dataframe(schema, use_container_width=True, hide_index=True)

    # Memory usage
    mem_mb = df.memory_usage(deep=True).sum() / 1_048_576
    st.caption(f"📦 Memory footprint: **{mem_mb:.2f} MB** · "
               f"Duplicate rows: **{dup_count}**")

    # Column type breakdown
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Numeric Columns**")
        tags = " ".join(f'<span class="tag">{c}</span>' for c in num_cols) or "<em>None</em>"
        st.markdown(tags, unsafe_allow_html=True)
    with col2:
        st.markdown("**Categorical Columns**")
        tags = " ".join(f'<span class="tag tag-amber">{c}</span>' for c in cat_cols) or "<em>None</em>"
        st.markdown(tags, unsafe_allow_html=True)

    # Full data preview
    with st.expander("🔎 Full Dataset Preview"):
        n = st.slider("Rows to show", 5, min(500, len(df)), 20, key="preview_slider")
        st.dataframe(df.head(n), use_container_width=True)

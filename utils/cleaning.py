"""
utils/cleaning.py
Data quality analysis: missing values, duplicates, outliers, and recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# ─── Plotly Dark Theme ────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,0.9)",
    font=dict(family="IBM Plex Mono", color="#8b949e", size=11),
    colorway=["#3ddbd9", "#e6a817", "#a371f7", "#f85149", "#3fb950"],
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    margin=dict(l=40, r=20, t=40, b=40),
)


def analyze_data_quality(df: pd.DataFrame):
    """Full data quality report with charts and AI-style recommendations."""

    # ── Missing Values ──────────────────────────────────────────────────────
    st.markdown("### 🕳 Missing Value Analysis")

    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "Column": missing.index,
        "Missing Count": missing.values,
        "Missing %": missing_pct.values,
    }).sort_values("Missing %", ascending=False)
    missing_df = missing_df[missing_df["Missing Count"] > 0]

    if missing_df.empty:
        st.success("✅ No missing values detected. Dataset is complete!")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = go.Figure(go.Bar(
                x=missing_df["Missing %"],
                y=missing_df["Column"],
                orientation="h",
                marker=dict(
                    color=missing_df["Missing %"],
                    colorscale=[[0, "#3ddbd9"], [0.5, "#e6a817"], [1, "#f85149"]],
                    showscale=True,
                    colorbar=dict(title="Miss %"),
                ),
                text=missing_df["Missing %"].astype(str) + "%",
                textposition="outside",
            ))
            fig.update_layout(**PLOTLY_LAYOUT, title="Missing Values by Column",
                              height=max(300, len(missing_df) * 30 + 100))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Missing Data Summary**")
            st.dataframe(missing_df, use_container_width=True, hide_index=True)

        # Recommendations
        st.markdown("#### 💡 Handling Recommendations")
        for _, row in missing_df.iterrows():
            col = row["Column"]
            pct = row["Missing %"]
            dtype = str(df[col].dtype)

            if pct > 50:
                advice = f'<span class="tag tag-danger">HIGH</span> **{col}** ({pct}% missing) — Consider dropping this column or using advanced imputation (KNN, MICE).'
            elif pct > 20:
                advice = f'<span class="tag tag-amber">MED</span> **{col}** ({pct}% missing) — Use median/mode imputation or model-based imputation.'
            else:
                if "float" in dtype or "int" in dtype:
                    advice = f'<span class="tag tag-success">LOW</span> **{col}** ({pct}% missing, numeric) — Mean/median imputation is safe here.'
                else:
                    advice = f'<span class="tag tag-success">LOW</span> **{col}** ({pct}% missing, categorical) — Fill with mode or an "Unknown" category.'

            st.markdown(advice, unsafe_allow_html=True)

    st.markdown("---")

    # ── Duplicate Rows ──────────────────────────────────────────────────────
    st.markdown("### 📋 Duplicate Row Analysis")
    dup_count = df.duplicated().sum()
    dup_pct   = round(dup_count / len(df) * 100, 2)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rows",    f"{len(df):,}")
    c2.metric("Duplicate Rows", f"{dup_count:,}")
    c3.metric("Duplicate %",   f"{dup_pct}%")

    if dup_count > 0:
        st.warning(f"⚠️ Found **{dup_count}** duplicate rows ({dup_pct}%). "
                   "Remove duplicates with `df.drop_duplicates()` before training any model.")
        with st.expander("View duplicate rows"):
            st.dataframe(df[df.duplicated(keep=False)].head(50), use_container_width=True)
    else:
        st.success("✅ No duplicate rows found.")

    st.markdown("---")

    # ── Outlier Detection (IQR method) ──────────────────────────────────────
    st.markdown("### 📡 Outlier Detection (IQR Method)")

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not num_cols:
        st.info("No numeric columns to analyse for outliers.")
        return

    outlier_summary = []
    for col in num_cols:
        series = df[col].dropna()
        Q1, Q3  = series.quantile(0.25), series.quantile(0.75)
        IQR     = Q3 - Q1
        lo, hi  = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        n_out   = int(((series < lo) | (series > hi)).sum())
        pct_out = round(n_out / len(series) * 100, 2)
        outlier_summary.append({
            "Column": col, "Q1": round(Q1, 3), "Q3": round(Q3, 3),
            "IQR": round(IQR, 3), "Lower Fence": round(lo, 3),
            "Upper Fence": round(hi, 3), "Outliers": n_out,
            "Outlier %": pct_out,
        })

    out_df = pd.DataFrame(outlier_summary).sort_values("Outlier %", ascending=False)
    st.dataframe(out_df, use_container_width=True, hide_index=True)

    # Interactive boxplot for outlier visualisation
    col_to_plot = st.selectbox("Select column to inspect with box plot", num_cols)
    fig2 = px.box(df, y=col_to_plot, points="outliers",
                  color_discrete_sequence=["#3ddbd9"])
    fig2.update_layout(**PLOTLY_LAYOUT, title=f"Box Plot — {col_to_plot}", height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Data-Type Overview ──────────────────────────────────────────────────
    st.markdown("### 🔠 Data Type Overview")
    dtype_counts = df.dtypes.astype(str).value_counts().reset_index()
    dtype_counts.columns = ["Data Type", "Count"]

    fig3 = px.pie(dtype_counts, names="Data Type", values="Count",
                  color_discrete_sequence=["#3ddbd9", "#e6a817", "#a371f7", "#f85149"])
    fig3.update_layout(**PLOTLY_LAYOUT, title="Column Data Type Distribution", height=350)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Overall Quality Score ────────────────────────────────────────────────
    st.markdown("### 🏆 Overall Data Quality Score")
    miss_score = max(0, 100 - missing_pct.mean() * 2)
    dup_score  = max(0, 100 - dup_pct * 5)
    out_score  = max(0, 100 - out_df["Outlier %"].mean())
    quality    = round((miss_score + dup_score + out_score) / 3, 1)

    color = "#3fb950" if quality >= 75 else ("#e6a817" if quality >= 50 else "#f85149")
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=quality,
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color=color),
            bgcolor="#161b22",
            steps=[
                dict(range=[0, 50],  color="rgba(248,81,73,.1)"),
                dict(range=[50, 75], color="rgba(230,168,23,.1)"),
                dict(range=[75, 100],color="rgba(63,185,80,.1)"),
            ],
            threshold=dict(line=dict(color="white", width=2), thickness=0.75, value=75),
        ),
        title=dict(text="Data Quality Score", font=dict(family="Syne", size=18)),
        number=dict(suffix="/100", font=dict(family="IBM Plex Mono", size=40)),
    ))
    fig4.update_layout(**PLOTLY_LAYOUT, height=320)
    st.plotly_chart(fig4, use_container_width=True)

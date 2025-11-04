"""
utils/statistics.py
Full statistical summary: descriptive stats, skewness, kurtosis, normality tests.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats as scipy_stats

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,0.9)",
    font=dict(family="IBM Plex Mono", color="#8b949e", size=11),
    colorway=["#3ddbd9", "#e6a817", "#a371f7", "#f85149", "#3fb950"],
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    margin=dict(l=40, r=20, t=40, b=40),
)


def generate_statistics(df: pd.DataFrame):
    """Display full statistical summary with interpretation hints."""

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not num_cols:
        st.warning("No numeric columns found for statistical analysis.")
        return

    # ── Descriptive Statistics ───────────────────────────────────────────────
    st.markdown("### 📐 Descriptive Statistics")

    desc = df[num_cols].describe().T
    desc["variance"] = df[num_cols].var().values
    desc["skewness"] = df[num_cols].skew().values
    desc["kurtosis"] = df[num_cols].kurt().values
    desc = desc[["count", "mean", "std", "variance", "min", "25%", "50%", "75%", "max", "skewness", "kurtosis"]]
    desc = desc.round(4)
    desc.index.name = "Column"
    st.dataframe(desc, use_container_width=True)

    st.markdown("---")

    # ── Skewness Analysis ────────────────────────────────────────────────────
    st.markdown("### 📉 Skewness & Kurtosis Analysis")

    skew_df = pd.DataFrame({
        "Column":   num_cols,
        "Skewness": [round(df[c].skew(), 4) for c in num_cols],
        "Kurtosis": [round(df[c].kurt(), 4) for c in num_cols],
    }).sort_values("Skewness", key=abs, ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig_skew = go.Figure(go.Bar(
            x=skew_df["Skewness"],
            y=skew_df["Column"],
            orientation="h",
            marker=dict(
                color=skew_df["Skewness"],
                colorscale=[[0, "#f85149"], [0.5, "#3ddbd9"], [1, "#a371f7"]],
                showscale=True,
            ),
        ))
        fig_skew.update_layout(**PLOTLY_LAYOUT, title="Skewness per Column",
                               height=max(300, len(num_cols) * 28 + 80))
        st.plotly_chart(fig_skew, use_container_width=True)

    with col2:
        fig_kurt = go.Figure(go.Bar(
            x=skew_df["Kurtosis"],
            y=skew_df["Column"],
            orientation="h",
            marker=dict(
                color=skew_df["Kurtosis"],
                colorscale=[[0, "#3ddbd9"], [0.5, "#e6a817"], [1, "#f85149"]],
                showscale=True,
            ),
        ))
        fig_kurt.update_layout(**PLOTLY_LAYOUT, title="Kurtosis per Column",
                               height=max(300, len(num_cols) * 28 + 80))
        st.plotly_chart(fig_kurt, use_container_width=True)

    # Interpretations
    st.markdown("#### 📖 Interpretation Guide")
    for _, row in skew_df.iterrows():
        sk = row["Skewness"]
        ku = row["Kurtosis"]
        skew_label = (
            "Approximately symmetric" if abs(sk) < 0.5
            else ("Moderately skewed" if abs(sk) < 1.0
            else "Highly skewed")
        )
        direction = "right (positive)" if sk > 0 else ("left (negative)" if sk < 0 else "")
        kurtosis_label = (
            "Leptokurtic (heavy tails)" if ku > 1
            else ("Platykurtic (light tails)" if ku < -1
            else "Mesokurtic (normal-like)")
        )
        st.markdown(
            f'<div class="insight-item"><span class="ins-num">SK</span>'
            f'<strong>{row["Column"]}</strong>: {skew_label}'
            f'{" — " + direction if direction else ""} · {kurtosis_label}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Normality Tests ──────────────────────────────────────────────────────
    st.markdown("### 🧪 Normality Tests (Shapiro-Wilk for n≤5000)")

    norm_rows = []
    for col in num_cols:
        sample = df[col].dropna()
        if len(sample) < 3:
            continue
        n = min(len(sample), 5000)
        stat, p = scipy_stats.shapiro(sample.sample(n, random_state=42))
        norm_rows.append({
            "Column": col,
            "W-statistic": round(stat, 4),
            "p-value": round(p, 4),
            "Normal?": "✅ Yes" if p > 0.05 else "❌ No",
        })

    if norm_rows:
        norm_df = pd.DataFrame(norm_rows)
        st.dataframe(norm_df, use_container_width=True, hide_index=True)
        st.caption("p > 0.05 → fail to reject normality (approximately normal at 5% significance).")

    st.markdown("---")

    # ── Distribution Inspector ───────────────────────────────────────────────
    st.markdown("### 🔬 Distribution Inspector")

    sel_col = st.selectbox("Select a numeric column", num_cols, key="dist_col")
    series  = df[sel_col].dropna()

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=series, nbinsx=40, name="Frequency",
        marker_color="#3ddbd9", opacity=0.75,
    ))
    # Overlay KDE using scipy
    kde_x = np.linspace(series.min(), series.max(), 300)
    kde   = scipy_stats.gaussian_kde(series)
    scale = len(series) * (series.max() - series.min()) / 40
    fig_dist.add_trace(go.Scatter(
        x=kde_x, y=kde(kde_x) * scale, mode="lines",
        name="KDE", line=dict(color="#e6a817", width=2),
    ))
    fig_dist.update_layout(**PLOTLY_LAYOUT, title=f"Distribution of {sel_col}",
                           barmode="overlay", height=380)
    st.plotly_chart(fig_dist, use_container_width=True)

    # Quick stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean",   f"{series.mean():.4f}")
    c2.metric("Median", f"{series.median():.4f}")
    c3.metric("Std Dev",f"{series.std():.4f}")
    try:
        mode_val = series.mode().iloc[0]
        c4.metric("Mode", f"{mode_val:.4f}")
    except Exception:
        c4.metric("Mode", "N/A")

    st.markdown("---")

    # ── Categorical Column Summary ───────────────────────────────────────────
    if cat_cols:
        st.markdown("### 🗂 Categorical Column Summary")
        sel_cat = st.selectbox("Select a categorical column", cat_cols, key="cat_col")
        vc = df[sel_cat].value_counts().head(20).reset_index()
        vc.columns = ["Value", "Count"]

        fig_cat = px.bar(vc, x="Count", y="Value", orientation="h",
                         color="Count",
                         color_continuous_scale=[[0, "#3ddbd9"], [1, "#a371f7"]])
        fig_cat.update_layout(**PLOTLY_LAYOUT, title=f"Top Values — {sel_cat}", height=400)
        st.plotly_chart(fig_cat, use_container_width=True)

        st.metric("Unique Values", df[sel_cat].nunique())

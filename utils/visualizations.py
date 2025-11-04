"""
utils/visualizations.py
Comprehensive visualization suite: histogram, boxplot, scatter, heatmap,
correlation matrix, pair plot, and count plots — all in Plotly dark theme.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,0.9)",
    font=dict(family="IBM Plex Mono", color="#8b949e", size=11),
    colorway=["#3ddbd9", "#e6a817", "#a371f7", "#f85149", "#3fb950",
              "#58a6ff", "#ff7b72", "#ffa657"],
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    margin=dict(l=40, r=20, t=50, b=40),
)


def run_visualizations(df: pd.DataFrame):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    tabs = st.tabs([
        "📊 Histogram",
        "📦 Box Plot",
        "🔵 Scatter",
        "🌡 Heatmap / Corr",
        "📈 Count Plot",
        "🔗 Pair Plot",
    ])

    # ── Tab 1: Histogram ─────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("#### Histogram — Distribution of a Numeric Column")
        if not num_cols:
            st.info("No numeric columns available."); return

        col_h = st.selectbox("Column", num_cols, key="hist_col")
        bins  = st.slider("Number of bins", 10, 100, 30, key="hist_bins")
        color_h = st.selectbox("Color by (categorical)", ["None"] + cat_cols, key="hist_color")

        fig = px.histogram(
            df, x=col_h, nbins=bins,
            color=(None if color_h == "None" else color_h),
            marginal="box",
            opacity=0.75,
            color_discrete_sequence=["#3ddbd9", "#e6a817", "#a371f7", "#f85149"],
            title=f"Distribution of {col_h}",
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="ai-box">
        <strong>📖 What this chart tells you:</strong><br>
        A histogram shows how often each range of values appears in the data.
        A bell-shaped curve suggests the data is normally distributed.
        Long tails indicate skewness. Multiple peaks (bimodal/multimodal) may
        suggest different subpopulations within the data — worth investigating!
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 2: Box Plot ──────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("#### Box Plot — Spread, Median, and Outliers")
        if not num_cols:
            st.info("No numeric columns."); return

        col_b  = st.selectbox("Column", num_cols, key="box_col")
        grp_b  = st.selectbox("Group by (optional)", ["None"] + cat_cols, key="box_grp")

        fig2 = px.box(
            df, y=col_b,
            x=(None if grp_b == "None" else grp_b),
            color=(None if grp_b == "None" else grp_b),
            points="outliers",
            color_discrete_sequence=["#3ddbd9", "#e6a817", "#a371f7", "#f85149"],
            title=f"Box Plot — {col_b}" + (f" by {grp_b}" if grp_b != "None" else ""),
        )
        fig2.update_layout(**PLOTLY_LAYOUT, height=450)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        <div class="ai-box">
        <strong>📖 What this chart tells you:</strong><br>
        The box shows the interquartile range (IQR: Q1–Q3); the line inside is the median.
        Whiskers extend to the fences (1.5×IQR). Points beyond the whiskers are
        <strong>outliers</strong> — data points that deviate significantly from the rest.
        Wide boxes mean high variability; narrow boxes mean the data is concentrated.
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 3: Scatter Plot ──────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("#### Scatter Plot — Relationship Between Two Variables")
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns."); return

        c1, c2, c3 = st.columns(3)
        x_col = c1.selectbox("X-axis", num_cols, key="scat_x")
        y_col = c2.selectbox("Y-axis", num_cols, index=min(1, len(num_cols)-1), key="scat_y")
        color_s = c3.selectbox("Color by", ["None"] + cat_cols + num_cols, key="scat_c")

        sample_n = min(5000, len(df))
        df_s = df.sample(sample_n, random_state=42) if len(df) > sample_n else df

        fig3 = px.scatter(
            df_s, x=x_col, y=y_col,
            color=(None if color_s == "None" else color_s),
            trendline="ols",
            trendline_color_override="#e6a817",
            opacity=0.6,
            color_discrete_sequence=["#3ddbd9", "#e6a817", "#a371f7"],
            color_continuous_scale="teal",
            title=f"{y_col} vs {x_col}",
        )
        fig3.update_layout(**PLOTLY_LAYOUT, height=450)
        st.plotly_chart(fig3, use_container_width=True)

        # Pearson correlation
        corr_val = df[[x_col, y_col]].dropna().corr().iloc[0, 1]
        strength = (
            "strong positive" if corr_val > 0.7 else
            "moderate positive" if corr_val > 0.4 else
            "weak positive" if corr_val > 0.1 else
            "strong negative" if corr_val < -0.7 else
            "moderate negative" if corr_val < -0.4 else
            "weak negative" if corr_val < -0.1 else
            "near-zero (no linear)"
        )
        st.markdown(f"""
        <div class="ai-box">
        <strong>Pearson Correlation: {corr_val:.4f}</strong> — {strength} relationship.<br><br>
        The trendline (OLS) shows the best-fit linear relationship.
        Correlation ≠ causation; a high r-value means two features move together,
        not that one <em>causes</em> the other. Always check for confounders!
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 4: Heatmap / Correlation Matrix ──────────────────────────────────
    with tabs[3]:
        st.markdown("#### Correlation Heatmap — All Numeric Features")
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns."); return

        max_cols = st.slider("Max columns to include", 2, min(30, len(num_cols)), min(15, len(num_cols)), key="hm_cols")
        selected = num_cols[:max_cols]
        corr_matrix = df[selected].corr().round(3)

        fig4 = go.Figure(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale=[[0, "#f85149"], [0.5, "#161b22"], [1, "#3ddbd9"]],
            zmin=-1, zmax=1,
            text=corr_matrix.values.round(2),
            texttemplate="%{text}",
            textfont=dict(size=9),
            colorbar=dict(title="Corr", tickfont=dict(family="IBM Plex Mono")),
        ))
        fig4.update_layout(**PLOTLY_LAYOUT, title="Pearson Correlation Matrix",
                           height=max(450, len(selected) * 30 + 100))
        st.plotly_chart(fig4, use_container_width=True)

        # Top correlated pairs
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        pairs = upper.stack().reset_index()
        pairs.columns = ["Feature A", "Feature B", "Correlation"]
        pairs = pairs.reindex(pairs["Correlation"].abs().sort_values(ascending=False).index)

        st.markdown("**Top correlated pairs:**")
        st.dataframe(pairs.head(10), use_container_width=True, hide_index=True)

        st.markdown("""
        <div class="ai-box">
        <strong>📖 Reading the heatmap:</strong><br>
        Values close to <strong>+1</strong> (teal) → strong positive correlation<br>
        Values close to <strong>-1</strong> (red) → strong negative correlation<br>
        Values near <strong>0</strong> (dark) → no linear relationship<br><br>
        Highly correlated features (|r| > 0.9) may cause <em>multicollinearity</em> issues
        in linear models. Consider keeping only one of them or using PCA.
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 5: Count Plot ────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("#### Count Plot — Categorical Value Frequencies")
        if not cat_cols:
            st.info("No categorical columns detected."); return

        col_cp = st.selectbox("Categorical column", cat_cols, key="cp_col")
        top_n  = st.slider("Show top N values", 5, 50, 15, key="cp_n")
        vc     = df[col_cp].value_counts().head(top_n).reset_index()
        vc.columns = ["Value", "Count"]

        fig5 = px.bar(
            vc, x="Value", y="Count",
            color="Count",
            color_continuous_scale=[[0, "#3ddbd9"], [0.5, "#a371f7"], [1, "#e6a817"]],
            title=f"Top {top_n} Values in '{col_cp}'",
        )
        fig5.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig5, use_container_width=True)

        # Class balance check
        total = vc["Count"].sum()
        majority_pct = vc["Count"].max() / total * 100
        if majority_pct > 80:
            st.error(f"⚠️ Severe class imbalance! Top category accounts for {majority_pct:.1f}% of all values.")
        elif majority_pct > 60:
            st.warning(f"Moderate imbalance: top category = {majority_pct:.1f}%.")
        else:
            st.success("✅ Reasonably balanced category distribution.")

    # ── Tab 6: Pair Plot ─────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("#### Pair Plot — Multi-variable Relationships")
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns."); return

        max_p  = min(6, len(num_cols))
        sel_pp = st.multiselect("Select columns (max 6)", num_cols,
                                default=num_cols[:min(4, len(num_cols))], key="pp_cols")
        color_pp = st.selectbox("Color by", ["None"] + cat_cols, key="pp_color")

        if len(sel_pp) < 2:
            st.info("Select at least 2 columns."); return

        sample_pp = min(1000, len(df))
        df_pp = df.sample(sample_pp, random_state=42) if len(df) > sample_pp else df

        fig6 = px.scatter_matrix(
            df_pp,
            dimensions=sel_pp,
            color=(None if color_pp == "None" else color_pp),
            color_discrete_sequence=["#3ddbd9", "#e6a817", "#a371f7", "#f85149"],
            opacity=0.5,
            title="Scatter Matrix (Pair Plot)",
        )
        fig6.update_traces(diagonal_visible=True, showupperhalf=False)
        fig6.update_layout(**PLOTLY_LAYOUT, height=700)
        st.plotly_chart(fig6, use_container_width=True)

        st.markdown("""
        <div class="ai-box">
        <strong>📖 How to read a pair plot:</strong><br>
        Each cell shows a scatter plot between two features. Diagonal cells show
        the feature's own distribution. Clusters in any scatter cell suggest
        natural groupings in the data — useful for clustering tasks. Diagonal
        patterns suggest linear relationships — potential for regression or classification.
        </div>
        """, unsafe_allow_html=True)

"""
utils/ml_suggester.py
Rule-based ML algorithm recommendation engine with academic explanations.
"""

import streamlit as st
import pandas as pd
import numpy as np


# ── Algorithm Catalogue ──────────────────────────────────────────────────────
ALGORITHMS = {
    "classification": [
        {
            "name": "Random Forest",
            "emoji": "🌲",
            "tag": "Ensemble · Tree-based",
            "when": "General purpose; works well with mixed types and missing data.",
            "pros": "Robust to overfitting, handles non-linearity, provides feature importance.",
            "cons": "Slower inference on large forests; less interpretable than a single tree.",
        },
        {
            "name": "XGBoost / LightGBM",
            "emoji": "⚡",
            "tag": "Gradient Boosting",
            "when": "Tabular data competitions; outperforms most models on structured data.",
            "pros": "State-of-the-art accuracy, built-in regularisation, fast training.",
            "cons": "Many hyperparameters to tune; can overfit with small datasets.",
        },
        {
            "name": "Logistic Regression",
            "emoji": "📈",
            "tag": "Linear · Interpretable",
            "when": "Binary or multi-class problems where interpretability matters.",
            "pros": "Fast, probabilistic output, highly interpretable coefficients.",
            "cons": "Assumes linear decision boundary; struggles with complex patterns.",
        },
        {
            "name": "Support Vector Machine (SVM)",
            "emoji": "🔷",
            "tag": "Kernel Method",
            "when": "High-dimensional, small-to-medium datasets.",
            "pros": "Effective in high-dimensional spaces; memory efficient.",
            "cons": "Slow on large datasets; sensitive to feature scaling.",
        },
        {
            "name": "K-Nearest Neighbors",
            "emoji": "📍",
            "tag": "Instance-based",
            "when": "Small datasets with clear local structure.",
            "pros": "Simple, no training phase, naturally handles multi-class.",
            "cons": "Slow prediction at scale; sensitive to irrelevant features.",
        },
    ],
    "regression": [
        {
            "name": "Linear Regression",
            "emoji": "📏",
            "tag": "Linear · Interpretable",
            "when": "Target has approximately linear relationship with features.",
            "pros": "Extremely interpretable, fast, solid baseline.",
            "cons": "Assumes linearity; sensitive to outliers and multicollinearity.",
        },
        {
            "name": "Ridge / Lasso Regression",
            "emoji": "🔧",
            "tag": "Regularised Linear",
            "when": "Many features; especially when multicollinearity is detected.",
            "pros": "Lasso performs feature selection (sparse coefficients); Ridge handles correlated features.",
            "cons": "Still assumes linearity in the feature–target relationship.",
        },
        {
            "name": "Random Forest Regressor",
            "emoji": "🌲",
            "tag": "Ensemble · Non-linear",
            "when": "Non-linear regression with complex interactions between features.",
            "pros": "Handles non-linearity, robust to outliers, minimal preprocessing needed.",
            "cons": "Less interpretable; extrapolation beyond training range is unreliable.",
        },
        {
            "name": "XGBoost Regressor",
            "emoji": "⚡",
            "tag": "Gradient Boosting",
            "when": "Competitive regression tasks on structured/tabular data.",
            "pros": "Often best out-of-box on tabular data; handles missing values natively.",
            "cons": "Risk of overfitting without proper regularisation; needs tuning.",
        },
        {
            "name": "SVR (Support Vector Regression)",
            "emoji": "🔷",
            "tag": "Kernel Method",
            "when": "Small-to-medium datasets with non-linear patterns.",
            "pros": "Robust to outliers due to epsilon-insensitive loss.",
            "cons": "Slow on large datasets; requires feature scaling.",
        },
    ],
    "clustering": [
        {
            "name": "K-Means",
            "emoji": "🔵",
            "tag": "Partition-based",
            "when": "You expect roughly spherical, similarly-sized clusters.",
            "pros": "Fast, simple, scalable to large datasets.",
            "cons": "You must specify k; sensitive to outliers and scale.",
        },
        {
            "name": "DBSCAN",
            "emoji": "🌌",
            "tag": "Density-based",
            "when": "Clusters of arbitrary shape; presence of noise/outliers.",
            "pros": "Automatically finds number of clusters; robust to outliers.",
            "cons": "Struggles with varying density; two epsilon/minPts hyperparameters.",
        },
        {
            "name": "Hierarchical Clustering",
            "emoji": "🌳",
            "tag": "Agglomerative",
            "when": "You want a dendrogram / don't know k in advance.",
            "pros": "No k required; produces interpretable tree structure.",
            "cons": "O(n²) complexity; not scalable to very large datasets.",
        },
        {
            "name": "Gaussian Mixture Model",
            "emoji": "🎯",
            "tag": "Probabilistic",
            "when": "Soft cluster assignments / overlapping clusters.",
            "pros": "Provides probabilistic membership; handles elliptical clusters.",
            "cons": "Assumes Gaussian distributions; can converge to local optima.",
        },
    ],
}


def detect_target_column(df: pd.DataFrame) -> str | None:
    """
    Heuristically identify the most likely target column.
    Priority: columns named 'target', 'label', 'class', 'y', 'output', etc.
    Falls back to the last column.
    """
    # TODO: check column names against a keyword list (target, label, class,
    # output, price, sales, etc.), first for exact matches then substring
    # matches, falling back to the last column if nothing matches.
    return df.columns[-1]


def suggest_ml_algorithms(df: pd.DataFrame, target_col: str | None):
    """Display algorithm cards with explanations based on dataset characteristics."""

    # Target selection UI
    st.markdown("### 🎯 Target Column")
    all_cols = list(df.columns)
    default_idx = all_cols.index(target_col) if target_col in all_cols else len(all_cols) - 1
    target = st.selectbox(
        "Select the target (output) column",
        ["None — Unsupervised Task"] + all_cols,
        index=default_idx + 1,
        key="target_sel",
    )

    st.markdown("---")

    # ── Determine task type ──────────────────────────────────────────────────
    # TODO: if target is "None — Unsupervised Task", set task = "clustering";
    # otherwise inspect df[target] — if non-numeric or few unique values,
    # task = "classification", else task = "regression".
    task = "classification"
    task_label = "Classification"

    # Dataset characteristics summary
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    n_rows, n_cols = df.shape
    miss_pct = df.isnull().mean().mean() * 100
    has_missing = miss_pct > 5

    st.markdown(f"### 🤖 Recommended Algorithms for **{task_label}**")

    c1, c2, c3 = st.columns(3)
    c1.metric("Task Detected",   task_label)
    c2.metric("Dataset Size",    f"{n_rows:,} rows")
    c3.metric("Features",        f"{n_cols - (1 if target != 'None — Unsupervised Task' else 0)}")

    st.markdown("---")

    # ── Algorithm Cards ──────────────────────────────────────────────────────
    for alg in ALGORITHMS[task]:
        with st.expander(f"{alg['emoji']}  {alg['name']}  ·  `{alg['tag']}`"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**When to use:**  \n{alg['when']}")
                st.markdown(f"**Advantages:**  \n{alg['pros']}")
            with col2:
                st.markdown(f"**Limitations:**  \n{alg['cons']}")

                # Context-aware notes
                notes = []
                if has_missing:
                    if alg["name"] in ["Random Forest", "XGBoost / LightGBM", "XGBoost Regressor"]:
                        notes.append("✅ Handles missing values natively — good choice for this dataset.")
                    else:
                        notes.append("⚠️ This algorithm requires imputation first (dataset has missing values).")
                if n_rows > 100_000:
                    if alg["name"] in ["SVM", "Support Vector Machine (SVM)", "SVR (Support Vector Regression)"]:
                        notes.append("⚠️ Large dataset detected — SVM will be slow. Consider tree-based methods.")
                    if alg["name"] in ["K-Nearest Neighbors"]:
                        notes.append("⚠️ KNN is O(n) at prediction time — may be slow on 100k+ rows.")

                if notes:
                    for n in notes:
                        st.markdown(n)

    st.markdown("---")

    # ── Preprocessing Checklist ──────────────────────────────────────────────
    st.markdown("### 🧹 Recommended Preprocessing Steps")

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    steps = []

    # TODO: build the `steps` list based on dataset characteristics —
    # missing-value imputation if has_missing, categorical encoding if
    # cat_cols is non-empty, feature scaling if there's more than one numeric
    # column, and class-imbalance handling if the task is classification and
    # the target's majority class exceeds 80%.

    for title, desc in steps:
        st.markdown(f'<div class="insight-item"><span class="ins-num">→</span>'
                    f'<strong>{title}</strong>: {desc}</div>', unsafe_allow_html=True)

    if not steps:
        st.success("✅ Dataset looks clean! Minimal preprocessing needed.")

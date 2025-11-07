"""
utils/feature_importance.py
Train a lightweight Random Forest to extract feature importances.
Works for both classification and regression targets.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,0.9)",
    font=dict(family="IBM Plex Mono", color="#8b949e", size=11),
    colorway=["#3ddbd9", "#e6a817", "#a371f7", "#f85149", "#3fb950"],
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    margin=dict(l=40, r=20, t=50, b=40),
)


def _prepare_features(df: pd.DataFrame, target: str):
    """
    Prepare X and y for sklearn:
    - Drops rows where target is null
    - Label-encodes categoricals in X
    - Fills remaining NaN with column medians/modes
    """
    data = df.dropna(subset=[target]).copy()
    y_raw = data[target]
    X_raw = data.drop(columns=[target])

    # Drop columns with >50% missing
    X_raw = X_raw.loc[:, X_raw.isnull().mean() < 0.5]

    # Encode categoricals
    for col in X_raw.select_dtypes(include=["object", "category"]).columns:
        le = LabelEncoder()
        X_raw[col] = le.fit_transform(X_raw[col].astype(str))

    # Fill numeric NaN with median
    for col in X_raw.select_dtypes(include=np.number).columns:
        X_raw[col].fillna(X_raw[col].median(), inplace=True)

    # Encode target if categorical
    is_classification = not pd.api.types.is_numeric_dtype(y_raw) or y_raw.nunique() <= 20
    if not pd.api.types.is_numeric_dtype(y_raw):
        le_y = LabelEncoder()
        y = le_y.fit_transform(y_raw.astype(str))
    else:
        y = y_raw.values

    return X_raw, y, is_classification


def compute_feature_importance(df: pd.DataFrame):
    """UI + computation for feature importance analysis."""

    st.markdown("### 🎯 Select Target Column")
    all_cols = list(df.columns)
    target = st.selectbox(
        "Target column (what you want to predict)",
        all_cols,
        index=len(all_cols) - 1,
        key="fi_target",
    )

    n_estimators = st.slider("Number of trees (more = accurate but slower)", 50, 300, 100, 50, key="fi_trees")

    if st.button("🚀 Train Model & Compute Feature Importance", use_container_width=True):
        with st.spinner("Training Random Forest… this may take a moment."):
            try:
                X, y, is_classification = _prepare_features(df, target)

                if X.shape[1] == 0:
                    st.error("No valid feature columns found after preprocessing.")
                    return

                # Cap dataset size for speed
                max_n = 50_000
                if len(X) > max_n:
                    idx = np.random.choice(len(X), max_n, replace=False)
                    X, y = X.iloc[idx], y[idx]

                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                model = (
                    RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
                    if is_classification
                    else RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
                )
                model.fit(X_train, y_train)

                # Score
                y_pred = model.predict(X_test)
                if is_classification:
                    score = accuracy_score(y_test, y_pred)
                    score_label = f"Test Accuracy: {score*100:.2f}%"
                else:
                    score = r2_score(y_test, y_pred)
                    score_label = f"Test R² Score: {score:.4f}"

            except Exception as e:
                st.error(f"Model training failed: {e}")
                return

        st.success(f"✅ Model trained! {score_label}")

        # ── Feature Importance Chart ─────────────────────────────────────────
        importances = pd.Series(model.feature_importances_, index=X.columns)
        importances = importances.sort_values(ascending=True)

        st.markdown("---")
        st.markdown("### 📊 Feature Importance Ranking")

        fig = go.Figure(go.Bar(
            x=importances.values,
            y=importances.index,
            orientation="h",
            marker=dict(
                color=importances.values,
                colorscale=[[0, "#21262d"], [0.5, "#3ddbd9"], [1, "#a371f7"]],
                showscale=True,
                colorbar=dict(title="Importance"),
            ),
            text=[f"{v:.4f}" for v in importances.values],
            textposition="outside",
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title=f"Feature Importances (Random Forest · target='{target}')",
            height=max(400, len(importances) * 28 + 100),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Importance Table ─────────────────────────────────────────────────
        imp_df = pd.DataFrame({
            "Rank":       range(1, len(importances) + 1),
            "Feature":    importances.sort_values(ascending=False).index,
            "Importance": importances.sort_values(ascending=False).values.round(5),
            "Cumulative": np.cumsum(importances.sort_values(ascending=False).values).round(4),
        })
        st.dataframe(imp_df, use_container_width=True, hide_index=True)

        # ── Cumulative Importance ────────────────────────────────────────────
        st.markdown("### 📉 Cumulative Feature Importance")
        fig2 = px.area(
            imp_df, x="Feature", y="Cumulative",
            color_discrete_sequence=["#3ddbd9"],
            title="Cumulative Importance (sorted by importance)",
        )
        fig2.add_hline(y=0.8, line_dash="dot", line_color="#e6a817",
                       annotation_text="80% threshold")
        fig2.add_hline(y=0.95, line_dash="dot", line_color="#f85149",
                       annotation_text="95% threshold")
        fig2.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig2, use_container_width=True)

        # ── Insights ─────────────────────────────────────────────────────────
        st.markdown("### 💡 Feature Insights")
        top3 = imp_df.head(3)["Feature"].tolist()
        bottom3 = imp_df.tail(3)["Feature"].tolist()
        thresh_80 = int((imp_df["Cumulative"] <= 0.80).sum()) + 1

        st.markdown(f"""
        <div class="ai-box">
        <strong>🔑 Top predictors:</strong> {", ".join(top3)}<br>
        These features contribute most to the model's predictions. They should be prioritised
        in feature engineering and exploratory analysis.<br><br>

        <strong>🪶 Weak predictors:</strong> {", ".join(bottom3)}<br>
        These features add minimal predictive power. Consider removing them to reduce
        dimensionality and potential overfitting.<br><br>

        <strong>📦 Minimal feature set:</strong> Only <strong>{thresh_80}</strong> features
        are needed to capture 80% of the model's predictive power.
        This is your recommended feature set for a lean production model.<br><br>

        <strong>📈 Model performance:</strong> {score_label}
        </div>
        """, unsafe_allow_html=True)

        # Store importances in session state for PDF report
        st.session_state["fi_importances"] = imp_df.to_dict()
        st.session_state["fi_score"]       = score_label

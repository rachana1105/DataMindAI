"""
utils/ai_explainer.py
AI Professor explanation module.
Primary: Google Gemini API
Fallback: Rich rule-based engine (no API key required)
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional


# ─── Gemini API Call ──────────────────────────────────────────────────────────

def _call_gemini(prompt: str, api_key: str) -> str:
    """
    Call Google Gemini 1.5 Flash API and return the text response.
    Returns empty string on failure.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except ImportError:
        return ""
    except Exception as e:
        st.warning(f"Gemini API error: {e}. Falling back to built-in insights.")
        return ""


# ─── Dataset Summary Helper ───────────────────────────────────────────────────

def _summarise_dataset(df: pd.DataFrame) -> dict:
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    missing_pct  = df.isnull().mean().mean() * 100
    dup_count    = df.duplicated().sum()

    skew_values  = {c: round(df[c].skew(), 3) for c in num_cols if df[c].notna().sum() > 3}
    corr_pairs   = []
    if len(num_cols) >= 2:
        corr_matrix = df[num_cols].corr()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        pairs = upper.stack().reset_index()
        pairs.columns = ["A", "B", "r"]
        top_pairs = pairs.reindex(pairs["r"].abs().sort_values(ascending=False).index).head(5)
        corr_pairs = [f"{r.A}↔{r.B} (r={r.r:.3f})" for _, r in top_pairs.iterrows()]

    return {
        "shape":        df.shape,
        "num_cols":     num_cols,
        "cat_cols":     cat_cols,
        "missing_pct":  round(missing_pct, 2),
        "dup_count":    int(dup_count),
        "skew_values":  skew_values,
        "corr_pairs":   corr_pairs,
    }


# ─── Rule-Based Fallback Explanation ─────────────────────────────────────────

def _local_explanation(summary: dict) -> str:
    # TODO: build a "Professor's Analysis" narrative from `summary` — cover
    # dataset structure, data quality (missing values, duplicates),
    # distribution/skewness analysis, correlation insights, an ML task
    # recommendation, and a preprocessing checklist. Return the joined text.
    return "Professor's Analysis unavailable — implementation pending."


# ─── Main Explanation Function ────────────────────────────────────────────────

def generate_ai_explanation(df: pd.DataFrame, api_key: Optional[str] = None) -> str:
    summary = _summarise_dataset(df)

    if api_key:
        # TODO: build a prompt instructing Gemini to act as an ML professor
        # explaining the dataset (overview, quality, distribution/skew,
        # correlations, ML task recommendation, preprocessing pipeline,
        # expected challenges) using `summary`, then call _call_gemini().
        prompt = ""
        result = _call_gemini(prompt, api_key)
        if result:
            return result

    # Fallback
    return _local_explanation(summary)


# ─── Auto-Insights Generation ─────────────────────────────────────────────────

def _local_insights(df: pd.DataFrame) -> list[str]:
    """Generate up to 12 automatic insights from the dataset."""
    insights = []

    # TODO: inspect the dataframe and append plain-language insight strings
    # covering: dataset size (too large/small), missing-value rate, duplicate
    # rows, strong feature correlations, skewed numeric columns, high-cardinality
    # or ID-like categorical columns, class imbalance, constant columns, and
    # feature-to-sample ratio. Fall back to a couple of generic "looks clean"
    # messages if nothing notable is found. Return at most 12 insights.

    if not insights:
        insights.append("No critical issues detected! The dataset appears clean and well-structured.")

    return insights[:12]  # Cap at 12


def generate_insights(df: pd.DataFrame, api_key: Optional[str] = None) -> list[str]:
    """Return a list of insight strings (AI or rule-based)."""

    if api_key:
        summary   = _summarise_dataset(df)

        # TODO: build a prompt asking Gemini for exactly 10 concise,
        # actionable insights as a JSON array of strings, using `summary`,
        # then call _call_gemini() and parse the JSON response.
        prompt = ""
        raw = _call_gemini(prompt, api_key)
        if raw:
            try:
                # Strip markdown fences if present
                clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                parsed = json.loads(clean)
                if isinstance(parsed, list) and len(parsed) > 0:
                    return [str(i) for i in parsed]
            except Exception:
                pass  # fall through to local

    return _local_insights(df)

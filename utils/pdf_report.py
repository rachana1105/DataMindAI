"""
utils/pdf_report.py
Professional PDF report generation using ReportLab.
Includes: title page, dataset summary, quality metrics, statistics,
top insights, and ML recommendations.
"""

import io
import os
from datetime import datetime
from typing import Optional, Callable
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# ─── Colour Palette ───────────────────────────────────────────────────────────
TEAL   = colors.HexColor("#3ddbd9")
DARK   = colors.HexColor("#0d1117")
AMBER  = colors.HexColor("#e6a817")
MUTED  = colors.HexColor("#8b949e")
WHITE  = colors.white
LIGHT  = colors.HexColor("#e6edf3")
RED    = colors.HexColor("#f85149")
GREEN  = colors.HexColor("#3fb950")
PURP   = colors.HexColor("#a371f7")
PANEL  = colors.HexColor("#161b22")


def _styles():
    """Return a dict of named ParagraphStyles."""
    base = getSampleStyleSheet()
    return {
        "title":  ParagraphStyle("title",  fontSize=28, textColor=WHITE,
                                 fontName="Helvetica-Bold", alignment=TA_LEFT,
                                 spaceAfter=4),
        "sub":    ParagraphStyle("sub",    fontSize=13, textColor=TEAL,
                                 fontName="Helvetica", alignment=TA_LEFT,
                                 spaceAfter=2),
        "h2":     ParagraphStyle("h2",     fontSize=14, textColor=TEAL,
                                 fontName="Helvetica-Bold", spaceBefore=14,
                                 spaceAfter=6),
        "h3":     ParagraphStyle("h3",     fontSize=11, textColor=AMBER,
                                 fontName="Helvetica-Bold", spaceBefore=8,
                                 spaceAfter=4),
        "body":   ParagraphStyle("body",   fontSize=9,  textColor=LIGHT,
                                 fontName="Helvetica", leading=14,
                                 spaceAfter=4),
        "mono":   ParagraphStyle("mono",   fontSize=8,  textColor=MUTED,
                                 fontName="Courier", spaceAfter=3),
        "small":  ParagraphStyle("small",  fontSize=7,  textColor=MUTED,
                                 fontName="Helvetica", spaceAfter=2),
        "center": ParagraphStyle("center", fontSize=9,  textColor=LIGHT,
                                 alignment=TA_CENTER, fontName="Helvetica"),
        "tag_teal": ParagraphStyle("tag_teal", fontSize=8, textColor=TEAL,
                                   fontName="Helvetica-Bold"),
        "tag_red":  ParagraphStyle("tag_red",  fontSize=8, textColor=RED,
                                   fontName="Helvetica-Bold"),
        "tag_grn":  ParagraphStyle("tag_grn",  fontSize=8, textColor=GREEN,
                                   fontName="Helvetica-Bold"),
    }


def _dark_table(data, col_widths=None, header_bg=PANEL):
    """Build a dark-themed ReportLab Table."""
    tbl = Table(data, colWidths=col_widths)
    style = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  header_bg),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  TEAL),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("BACKGROUND",    (0, 1), (-1, -1), DARK),
        ("TEXTCOLOR",     (0, 1), (-1, -1), LIGHT),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [DARK, colors.HexColor("#0f1419")]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#21262d")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
    tbl.setStyle(style)
    return tbl


def generate_pdf_report(
    df: pd.DataFrame,
    filename: str = "dataset.csv",
    api_key: Optional[str] = None,
    progress_cb: Optional[Callable[[int], None]] = None,
) -> bytes:
    """
    Build and return a complete PDF report as bytes.
    progress_cb(0-100) is called at milestones.
    """
    from utils.ai_explainer import generate_ai_explanation, generate_insights

    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
        title="DataMind AI Report",
        author="DataMind AI Analyzer",
    )

    S = _styles()
    story = []
    W = A4[0] - 4*cm  # usable width

    def hr():
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#21262d"), spaceAfter=6))

    def sp(h=6):
        story.append(Spacer(1, h))

    # ── Title Page ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 40))

    title_data = [[
        Paragraph("DataMind AI", S["title"]),
        Paragraph("Dataset Analyzer Report", S["sub"]),
    ]]
    title_tbl = Table(title_data, colWidths=[W])
    title_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), DARK),
        ("TOPPADDING",  (0,0), (-1,-1), 18),
        ("BOTPADDING",  (0,0), (-1,-1), 18),  # type: ignore
        ("LEFTPADDING", (0,0), (-1,-1), 20),
    ]))
    story.append(title_tbl)
    sp(10)

    meta = [
        ["File", filename],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Rows", f"{df.shape[0]:,}"],
        ["Columns", f"{df.shape[1]}"],
    ]
    meta_tbl = _dark_table(meta, col_widths=[4*cm, W - 4*cm])
    story.append(meta_tbl)
    story.append(PageBreak())

    if progress_cb: progress_cb(10)

    # ── Dataset Overview ──────────────────────────────────────────────────────
    story.append(Paragraph("1. Dataset Overview", S["h2"]))
    hr()

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    miss_pct = df.isnull().mean().mean() * 100

    stats_data = [
        ["Metric", "Value"],
        ["Rows",              f"{df.shape[0]:,}"],
        ["Columns",           f"{df.shape[1]}"],
        ["Numeric Columns",   str(len(num_cols))],
        ["Categorical Cols",  str(len(cat_cols))],
        ["Missing Values %",  f"{miss_pct:.2f}%"],
        ["Duplicate Rows",    str(df.duplicated().sum())],
        ["Memory (MB)",       f"{df.memory_usage(deep=True).sum()/1_048_576:.2f}"],
    ]
    story.append(_dark_table(stats_data, col_widths=[6*cm, W - 6*cm]))
    sp()

    # Schema
    story.append(Paragraph("Column Schema", S["h3"]))
    schema_rows = [["Column", "Type", "Non-Null", "Null %", "Unique"]]
    for col in df.columns[:30]:  # cap at 30 cols for space
        schema_rows.append([
            col[:25],
            str(df[col].dtype),
            str(df[col].notnull().sum()),
            f"{df[col].isnull().mean()*100:.1f}%",
            str(df[col].nunique()),
        ])
    story.append(_dark_table(schema_rows, col_widths=[5*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm]))

    if progress_cb: progress_cb(25)
    story.append(PageBreak())

    # ── Data Quality ──────────────────────────────────────────────────────────
    story.append(Paragraph("2. Data Quality Analysis", S["h2"]))
    hr()

    # Missing by column
    missing_by_col = df.isnull().sum()
    missing_by_col = missing_by_col[missing_by_col > 0].sort_values(ascending=False)

    if len(missing_by_col) == 0:
        story.append(Paragraph("✓  No missing values detected. Dataset is complete.", S["body"]))
    else:
        story.append(Paragraph("Missing Values by Column", S["h3"]))
        miss_rows = [["Column", "Missing Count", "Missing %"]]
        for col, cnt in missing_by_col.head(20).items():
            pct = cnt / len(df) * 100
            miss_rows.append([col[:25], str(cnt), f"{pct:.2f}%"])
        story.append(_dark_table(miss_rows, col_widths=[7*cm, 4*cm, 4*cm]))

    sp(8)

    # Outlier summary
    story.append(Paragraph("Outlier Summary (IQR Method)", S["h3"]))
    out_rows = [["Column", "Outliers", "Outlier %", "Lower Fence", "Upper Fence"]]
    for col in num_cols[:15]:
        s = df[col].dropna()
        Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
        IQR = Q3 - Q1
        lo, hi = Q1 - 1.5*IQR, Q3 + 1.5*IQR
        n_out = int(((s < lo) | (s > hi)).sum())
        out_rows.append([
            col[:20], str(n_out),
            f"{n_out/len(s)*100:.2f}%",
            f"{lo:.3f}", f"{hi:.3f}",
        ])
    story.append(_dark_table(out_rows, col_widths=[5*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm]))

    if progress_cb: progress_cb(45)
    story.append(PageBreak())

    # ── Statistical Summary ───────────────────────────────────────────────────
    story.append(Paragraph("3. Statistical Summary", S["h2"]))
    hr()

    if num_cols:
        desc = df[num_cols[:10]].describe().T.round(3)
        stat_rows = [["Column"] + list(desc.columns)]
        for idx, row in desc.iterrows():
            stat_rows.append([str(idx)[:15]] + [f"{v:.3g}" for v in row.values])
        col_w = [3.5*cm] + [(W - 3.5*cm) / len(desc.columns)] * len(desc.columns)
        story.append(_dark_table(stat_rows, col_widths=col_w))

        sp(8)
        story.append(Paragraph("Skewness & Kurtosis", S["h3"]))
        sk_rows = [["Column", "Skewness", "Kurtosis", "Interpretation"]]
        for col in num_cols[:15]:
            sk = round(df[col].skew(), 4)
            ku = round(df[col].kurt(), 4)
            interp = ("Symmetric" if abs(sk) < 0.5
                      else ("Moderately skewed" if abs(sk) < 1 else "Highly skewed"))
            sk_rows.append([col[:20], str(sk), str(ku), interp])
        story.append(_dark_table(sk_rows, col_widths=[5*cm, 3*cm, 3*cm, W-11*cm]))

    if progress_cb: progress_cb(60)
    story.append(PageBreak())

    # ── AI Insights ───────────────────────────────────────────────────────────
    story.append(Paragraph("4. AI-Generated Insights", S["h2"]))
    hr()

    from utils.ai_explainer import generate_insights, generate_ai_explanation
    insights = generate_insights(df, api_key)
    for i, insight in enumerate(insights, 1):
        row = [[
            Paragraph(f"{i:02d}", S["tag_teal"]),
            Paragraph(str(insight)[:300], S["body"]),
        ]]
        tbl = Table(row, colWidths=[1*cm, W - 1*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,-1), PANEL),
            ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#21262d")),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING",(0,0), (-1,-1), 8),
            ("TOPPADDING",  (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ]))
        story.append(tbl)
        sp(3)

    if progress_cb: progress_cb(75)
    story.append(PageBreak())

    # ── AI Professor Explanation ──────────────────────────────────────────────
    story.append(Paragraph("5. Professor's Analysis", S["h2"]))
    hr()

    explanation = generate_ai_explanation(df, api_key)
    for para in explanation.split("\n"):
        para = para.strip()
        if not para:
            sp(4)
        elif para.startswith(("──", "─")):
            hr()
        elif para.isupper() and len(para) < 50:
            story.append(Paragraph(para, S["h3"]))
        else:
            story.append(Paragraph(para, S["body"]))

    if progress_cb: progress_cb(88)
    story.append(PageBreak())

    # ── ML Recommendations ────────────────────────────────────────────────────
    story.append(Paragraph("6. ML Algorithm Recommendations", S["h2"]))
    hr()

    # Determine likely task
    last_col = df.columns[-1]
    n_unique = df[last_col].nunique()
    is_num   = pd.api.types.is_numeric_dtype(df[last_col])
    task     = "Clustering" if (is_num and n_unique > 20) else "Classification/Regression"

    story.append(Paragraph(f"Detected task type: {task}", S["body"]))
    sp(8)

    alg_rows = [["Algorithm", "Type", "Best For"]]
    alg_data = [
        ("Random Forest",          "Ensemble",     "General purpose, mixed data"),
        ("XGBoost / LightGBM",     "Boosting",     "Competitive tabular ML"),
        ("Logistic Regression",    "Linear",       "Interpretable binary/multi-class"),
        ("SVM",                    "Kernel",       "High-dimensional, small datasets"),
        ("K-Means",                "Clustering",   "Spherical clusters, known k"),
        ("DBSCAN",                 "Clustering",   "Arbitrary shape, noisy data"),
        ("Linear Regression",      "Linear",       "Numeric target, linear relationship"),
    ]
    for name, typ, bf in alg_data:
        alg_rows.append([name, typ, bf])
    story.append(_dark_table(alg_rows, col_widths=[5.5*cm, 3*cm, W-8.5*cm]))

    sp(12)
    story.append(Paragraph("Preprocessing Checklist", S["h3"]))
    checks = [
        "Handle missing values (imputation or removal)",
        "Encode categorical variables (One-Hot / Label encoding)",
        "Scale numeric features for SVM, KNN, Logistic Regression",
        "Remove duplicate rows before training",
        "Split data BEFORE applying any transformations",
        "Address class imbalance if target is categorical",
        "Apply log/Box-Cox transform for highly skewed features",
    ]
    for c in checks:
        story.append(Paragraph(f"• {c}", S["body"]))

    # ── Footer ────────────────────────────────────────────────────────────────
    sp(20)
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
    story.append(Paragraph(
        f"Generated by DataMind AI Dataset Analyzer · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        S["small"],
    ))

    if progress_cb: progress_cb(95)

    doc.build(story)
    if progress_cb: progress_cb(100)

    return buf.getvalue()

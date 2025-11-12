# 🧠 DataMind AI — Dataset Analyzer

> **"Explain Dataset Like a Professor"**  
> Upload any CSV. Get AI-powered analysis, visualizations, ML suggestions, and a downloadable PDF report — instantly.

---

## 📸 Preview

```
┌─────────────────────────────────────────────────────────────┐
│  ⬡  DataMind AI    │  Dataset Overview                      │
│  Dataset Analyzer  │  ─────────────────────────────────     │
│  ─────────────────  │  Rows: 40,000   Cols: 15              │
│  📁 Upload          │  Missing: 2.1%  Numeric: 10           │
│  🔍 Data Overview   │                                        │
│  🧹 Data Quality    │  [Interactive Charts & Tables]         │
│  📊 Statistics      │                                        │
│  📈 Visualizations  │  AI Professor Explanation              │
│  🤖 ML Suggestions  │  ─────────────────────────────────     │
│  ⭐ Feature Import  │  "Good day, students. Let us           │
│  🧠 AI Insights     │   examine this dataset..."            │
│  📄 PDF Report      │                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Module | What it does |
|--------|-------------|
| **CSV Upload** | Drag & drop any CSV; auto-detects encoding (UTF-8, Latin-1, CP1252) |
| **Data Overview** | Schema, types, null counts, memory usage, sample values |
| **Data Quality** | Missing value heatmap, duplicate detection, outlier analysis (IQR), quality score gauge |
| **Statistics** | Descriptive stats, skewness, kurtosis, normality tests (Shapiro-Wilk), KDE plots |
| **Visualizations** | Histogram, Box plot, Scatter (with OLS trendline), Correlation heatmap, Count plot, Pair plot |
| **ML Suggestions** | Auto-detects task (classification/regression/clustering), recommends algorithms with pros/cons |
| **Feature Importance** | Trains a Random Forest, visualises importances, cumulative importance curve |
| **AI Insights** | Professor-style explanation via Gemini API (or local rule-based fallback) |
| **PDF Report** | Full professional report with all sections, dark theme, downloadable |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/rachana1105/DataMindAI.git
cd DataMindAI
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 🔑 API Key Setup (Optional)

AI-powered explanations use **Google Gemini 1.5 Flash** (free tier available).

**Option A — Enter in UI:**  
Just paste your key in the "AI Insights" or "PDF Report" section. No setup needed.

**Option B — Environment variable:**

1. Copy `.env` template:
   ```bash
   cp .env .env.local
   ```
2. Add your key:
   ```
   GEMINI_API_KEY=AIzaSy...
   ```
3. The app will auto-read it on startup.

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

> **Note:** The app works fully without an API key. Built-in rule-based insights cover all analysis sections.

---

## 📁 Project Structure

```
AI_Dataset_Analyzer/
│
├── app.py                          # Main Streamlit entry point
├── requirements.txt                # Python dependencies
├── .env                            # API key template
├── README.md                       # This file
│
├── .streamlit/
│   └── config.toml                 # Dark theme & server config
│
├── utils/
│   ├── __init__.py
│   ├── styles.py                   # Custom CSS injection
│   ├── data_loader.py              # CSV loading & overview
│   ├── cleaning.py                 # Quality analysis & outliers
│   ├── statistics.py               # Descriptive stats & normality
│   ├── visualizations.py           # All chart types (Plotly)
│   ├── ml_suggester.py             # Algorithm recommendation engine
│   ├── feature_importance.py       # Random Forest importance
│   ├── ai_explainer.py             # Gemini API + local fallback
│   └── pdf_report.py               # ReportLab PDF generation
│
├── assets/
│   └── sample_dataset.csv          # Demo dataset (income/loan data)
│
├── reports/                        # Generated PDF reports (auto-created)
├── uploads/                        # Temporary upload cache (optional)
├── visualizations/                 # Saved chart images (optional)
└── models/                         # Saved model files (optional)
```

---

## 📦 Dependencies

```
streamlit>=1.35.0       # UI framework
pandas>=2.0.0           # Data manipulation
numpy>=1.26.0           # Numerical computing
scipy>=1.12.0           # Statistical tests
scikit-learn>=1.4.0     # ML models & preprocessing
matplotlib>=3.8.0       # Static charts
seaborn>=0.13.0         # Statistical visualisation
plotly>=5.20.0          # Interactive charts
reportlab>=4.1.0        # PDF generation
google-generativeai>=0.7.0  # Gemini API
```

---

## 🌐 Deployment Guide

### Streamlit Community Cloud (Free)

1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Click "New app" → select your repo → `app.py`
4. Add `GEMINI_API_KEY` in **Secrets** (Settings → Secrets):
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   ```
5. Click **Deploy**

### Render

1. Create a new **Web Service** on https://render.com
2. Connect your GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add `GEMINI_API_KEY` in environment variables

### Hugging Face Spaces

1. Create a new Space at https://huggingface.co/spaces
2. Select **Streamlit** SDK
3. Upload all project files
4. Add `GEMINI_API_KEY` to Space **Secrets**

---

## 🧪 Testing with Sample Data

A sample dataset (`assets/sample_dataset.csv`) is included with:
- 40 rows, 10 columns
- Mixed numeric & categorical features
- Some missing values (for quality analysis demo)
- Target column: `loan_approved` (binary classification)

Download it from the **Upload Dataset** page using the "⬇ Download Sample CSV" button.

---

## 🎯 Use Cases

- 🎓 **Academic**: Final year project, dissertation data analysis
- 💼 **Internship/Job**: Portfolio showcase for ML/Data Science roles
- 🏆 **Hackathons**: Rapid dataset exploration and insight generation
- 🔬 **Research**: Quick EDA before deep analysis
- 📊 **Business**: Non-technical users exploring their own CSV data

---

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "Add: your feature"
git push origin feature/your-feature
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Author

Built with ❤️ using Streamlit, Plotly, scikit-learn, ReportLab, and Google Gemini.

> *"Data is the new oil, but only if you can understand it."*

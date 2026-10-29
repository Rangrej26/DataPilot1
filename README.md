# DataPilot AI — Your All-in-One Data Analyst Workspace

[![Python 3.10 - 3.13](https://img.shields.io/badge/Python-3.10%20--%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-In--Memory%20Analytics-FFF000.svg)](https://duckdb.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75.svg)](https://plotly.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML%20Pipelines-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-48%20Passed-brightgreen.svg)]()

> **Academic M.Sc. Data Science Project**  
> An end-to-end analytics workspace that transforms raw datasets into cleaned data, analytical SQL queries, guided visual charts, grounded AI insights, and evaluated machine learning predictions with concise explanations.
>
> Re-engineered with a high-performance **FastAPI** backend, modular REST architecture, and a modern, accessible **HTML5 / CSS3 / JavaScript** single-page frontend inspired by premium SaaS design standards.

---

## 🌟 Executive Summary

In routine data science, practitioners often switch between multiple disjointed tools: spreadsheets for manual inspection, database clients for SQL queries, Jupyter notebooks for modeling, and separate reporting scripts.

**DataPilot AI** unifies this lifecycle into a streamlined, high-performance, beginner-friendly workspace. Operating strictly on actual uploaded data, the application guides users through an 8-stage workflow:

$$\text{Upload \& Understand} \longrightarrow \text{Explore} \longrightarrow \text{Clean (Audited)} \longrightarrow \text{Chart Guide} \longrightarrow \text{SQL} \longrightarrow \text{AI Analyst} \longrightarrow \text{ML Lab} \longrightarrow \text{Export}$$

---

## 🎨 UI Design System & Strict Color Reference

The web application adheres strictly to the specified premium SaaS design reference palette:

| Surface / Element | Hex Color | Role |
|:---|:---:|:---|
| **Sidebar Background** | `#222225` | Dark charcoal sidebar for navigation and active dataset widget |
| **Main Workspace** | `#E8E8E8` | Soft light-grey background providing comfortable contrast |
| **Cards and Panels** | `#FFFFFF` | Crisp white content panels with subtle border demarcation |
| **Primary Text** | `#202124` | High-contrast dark charcoal text for titles, headings, and tables |
| **Secondary Text** | `#62636B` | Readable muted grey for subtitles, hints, and explanations |
| **Sidebar Primary Text** | `#FFFFFF` | High-contrast white for branding and active navigation |
| **Sidebar Secondary Text** | `#C6C6CC` | Muted silver for inactive navigation items and metadata |
| **Primary Accent** | `#D8F45B` | Lime-green accent for primary actions, badges, and highlights |
| **Secondary Accent** | `#B9ADF5` | Restrained lavender accent for categorical highlights and tags |
| **Borders** | `#D5D7DC` | Clean 1px structural dividing borders with 10px rounded corners |

---

## 🚀 Key Features

### 1. Intelligent Dataset Understanding & Semantic Column Dictionary
- **Automatic Dataset Understanding**:
  - Dynamically inspects column names, data types, sample values, and statistical distributions upon ingestion.
  - Generates a plain-English explanation of what the dataset represents.
  - Never hardcoded — adapts dynamically to any uploaded dataset.
- **Concise Dataset Overview**:
  - Displays high-level KPIs: dataset size (rows and columns), inferred domain/subject, and counts of numerical, categorical, and date features.
- **Semantic Column Dictionary**:
  - Explains each column's name, detected programmatic data type, inferred semantic meaning, safe sample value, and missing-value counts.
  - Distinguishes between software-detected programmatic types and AI/heuristic inferred semantic meanings.
- **Tailored Dynamic Analysis Suggestions**:
  - Recommends actionable analyses tailored strictly to the uploaded columns: categorical segmentation, chronological time-series trends, numerical correlation, and predictive machine learning tasks.
- **User-Friendly Context Injection**:
  - Allows users to provide optional background context (e.g., *"This dataset contains monthly sales records for my college project"*), tailoring insights without modifying underlying data.

### 2. Multi-Format Ingestion & Fast Metadata Profiling
- Ingests **CSV** (auto-delimiter and multi-encoding fallback) and **Multi-sheet Excel (.xlsx, .xls)** with worksheet selector.
- Enforces upload file-size validation (50MB default limit) and allowed extensions.
- Includes **4 pre-packaged realistic academic datasets** (1-click load):
  1. *E-Commerce Customer Churn* (1,542 rows — injected with real-world flaws: missing values, mixed date formats, casing discrepancies).
  2. *Employee HR & Attrition* (Multi-sheet Excel: `Employees` and `Department_Info`).
  3. *Medical Patient Health Risk* (1,200 rows — dual target for Regression and Classification).
  4. *Retail Performance Benchmark* (50,000 rows — verified sub-second DuckDB aggregation).

### 3. Smart Data Cleaning with 3-Part Explanations & Audit Trail
- **Compact Summary First**:
  - Displays a clean list of changes right after cleaning:
    - *12 missing values filled in 'Age'*
    - *42 duplicate rows removed*
    - *1 column converted to datetime*
  - If no cleaning was needed, clearly states: *"Your data looks good. No cleaning changes were necessary."*
- **Simple 3-Part Explanations**:
  - **What was found:** Plain-English description of the issue.
  - **What was changed:** Specific action taken and exact number of affected rows/values.
  - **Why:** Short, one-sentence plain-English justification.
- **Actionable Recommendations**:
  - Pre-screen issues with problem description, recommended action, reason, preview of effect, and **Apply Fix** buttons.
  - One-click **⚡ Auto-Clean All Confirmed Issues**.
- **Audit Trail & Reversibility**:
  - Maintains full historical audit records with timestamps and affected counts.
  - Supports single-click **↩ Undo Last Step** and **🔄 Reset to Original Data**.

### 4. Data Explorer & Profiling
- Interactive exploratory data analysis (EDA):
  - Paginated data table preview with multi-column text search.
  - Numerical descriptive statistics (Mean, Median, Std, Quartiles, Skewness, Zeros, IQR Outliers).
  - Categorical cardinality and top-frequency tables.
  - Interactive Plotly correlation heatmaps (Pearson / Spearman).
  - Missingness horizontal bar charts.
  - Single-feature distribution deep-dive (histograms + box plots for numbers, frequency bars for categories).

### 5. Beginner-Friendly Chart Guide & Visual Assistant
- **Dataset-Aware Guided Workflow**:
  1. *Understand User Goal*: Select from 6 analytical goals (Compare categories, Changes over time, Distributions & spread, Relationships, Proportions / composition, Data quality).
  2. *Schema Inspection*: Analyzes active columns, numerical vs. categorical counts, dates, and category cardinality.
  3. *Tailored Recommendations*: Generates cards explaining why a chart fits, required columns, axis roles, patterns to look for, and when to avoid.
  4. *Real Plotly Chart Generation*: Interactive Bar, Line, Histogram, Box, Scatter, Donut, Heatmap, and Missingness charts.
  5. *100% Grounded Mathematical Interpretation*: Automatically computes factual observations (highest/lowest categories, net change percentages, Pearson correlation coefficients) with zero fabrication.
- **Rule-Based & Offline**: Operates deterministically without external LLM API dependency.

### 6. DuckDB Analytical SQL Assistant & Security Sandbox
- High-performance in-memory analytical SQL powered by **DuckDB**.
- **Security Sandbox**: Strictly enforces read-only queries (`SELECT`, `WITH`). Blocks modifications (`DROP`, `DELETE`, `INSERT`) and unauthorized filesystem access (`read_csv`, `copy`, chained semicolons).
- Natural Language to SQL converter.
- Clause-by-clause beginner explanation (explaining `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`).
- Pre-built query templates adapted to schema columns.
- Results table with execution time in milliseconds (`ms`) and CSV export.

### 7. Grounded AI Data Analyst
- Ask analytical questions in plain English (*"Which category contributes most?", "Are there outliers?", "What are the strongest correlations?"*).
- **100% Deterministic Ground Truth**: Computes exact mathematics on Pandas/DuckDB without hallucinations.
- Starts with the single most important finding in bold, followed by concise bullet points with numbers.
- Auto-generates accompanying Plotly charts and data tables alongside text answers.
- Technical methodology and calculation formulas are tucked into an expandable **"How was this calculated?"** section.
- Optional LLM integration (Google Gemini, Groq, OpenAI) for executive summary synthesis when API keys are configured.

### 8. Scikit-Learn Machine Learning Lab & Predictive Studio
- **Automatic Task Detection & Strict Validation**:
  - Automatically infers Classification vs. Regression based on target datatype and cardinality.
  - Rejects string targets for Regression with instructional error messages.
  - Rejects continuous float targets with $> 25$ unique values for Classification.
- **Data & Target Leakage Prevention**:
  - Flags features with correlation $|r| \ge 0.95$ with the target.
  - Flags identifier columns (`_id`, `tracking_code`, UUIDs) to prevent memorization overfitting.
  - Strictly fits `ColumnTransformer` (Median Imputation + `StandardScaler`, Mode Imputation + `OneHotEncoder`) *only* on `X_train`.
- **Model Leaderboard**:
  - *Classification*: Random Forest, Gradient Boosting, Logistic Regression, Decision Tree (Accuracy, Precision, Recall, F1).
  - *Regression*: Random Forest, Gradient Boosting, Ridge, Linear Regression, Decision Tree ($R^2$, MAE, RMSE).
- **Diagnostic Visualizations**:
  - Confusion Matrix heatmap for classification.
  - Actual vs. Predicted scatter plot with 45-degree reference line for regression.
  - Top Feature Importances horizontal bar chart.
- **Interactive What-If Live Predictor**:
  - Real-time sliders and dropdown inputs to test live model predictions and class probabilities.
  - Guarded: Only accessible after successful model training.

### 9. Professional Reports & Exports
- **Academic PDF Dossier**: Vector-formatted PDF generated dynamically via **ReportLab** containing metadata, audit trail, statistical insights, and ML evaluations.
- **Multi-Tab Excel Workbook**: Generated via **OpenPyXL** containing Cleaned Data, Column Dictionary, Audit Trail, Numerical Profiling, and ML Leaderboard.
- Cleaned CSV export and SQL query result export.

---

## 📂 Project Architecture

```
minor_project/
├── backend/
│   ├── main.py                     # FastAPI application entry point, CORS & routing
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Environment configuration (.env)
│   ├── schemas/                    # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── datasets.py
│   │   ├── cleaning.py
│   │   ├── charts.py
│   │   ├── sql.py
│   │   ├── analyst.py
│   │   └── ml.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── dataset_store.py        # Isolated in-memory dataset session store with TTL
│   └── api/                        # REST API Routers
│       ├── __init__.py
│       ├── datasets.py             # Ingestion, profiling, previews, visualizations
│       ├── cleaning.py             # Detection, fixing, auto-clean, undo, reset
│       ├── charts.py               # Goals, recommendations, rendering, insights
│       ├── sql.py                  # Sandbox validation, execution, explainer
│       ├── analyst.py              # Natural language Q&A, grounded compute
│       ├── ml.py                   # Target inspection, training, leaderboard, inference
│       └── reports.py              # CSV, Excel, PDF dossier downloads
├── frontend/
│   ├── index.html                  # Single-Page Application (SPA) shell
│   ├── css/
│   │   └── styles.css              # Strict reference design system & Inter typography
│   └── js/
│       ├── api.js                  # Typed Fetch API client
│       └── app.js                  # State router, UI rendering, Plotly charts
├── modules/                        # Tested Python analytical engine
│   ├── __init__.py
│   ├── data_loader.py              # Ingestion, sheet extraction, metadata
│   ├── dataset_explainer.py        # Semantic profiler & analysis suggestions
│   ├── cleaning_engine.py          # Quality audit & atomic transformations
│   ├── chart_guide.py              # Recommendation logic & mathematical interpretation
│   ├── profiler.py                 # Descriptive statistics & correlation heatmaps
│   ├── sql_engine.py               # DuckDB connection & sandbox validation
│   ├── ai_analyst.py               # Grounded Q&A engine
│   ├── insights_engine.py          # Automated data stories
│   ├── ml_lab.py                   # Scikit-learn pipelines & live inference
│   ├── report_generator.py         # ReportLab PDF & OpenPyXL Excel generators
│   └── ui_components.py            # Theme definitions & color schemes
├── sample_data/                    # Pre-packaged academic test datasets
├── tests/                          # 48 Automated unit & integration tests
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── run_app.bat                     # 1-Click Windows Batch launcher
└── run_app.ps1                     # 1-Click PowerShell launcher
```

---

## ⚡ Installation & Run Instructions (Windows)

### Prerequisites
- Python 3.10 to 3.13 installed.
- Modern web browser (Chrome, Edge, Firefox).

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run Test Suite
Run the 48 automated unit and API integration tests:
```powershell
python -m pytest -v
```

### 3. Launch Application
You can launch using any of the following methods:

**Method 1: 1-Click Launcher (Recommended)**
- Double-click `run_app.bat` or run `.\run_app.ps1`.

**Method 2: Command Line**
```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to:
- **Web Application:** `http://127.0.0.1:8000`
- **Interactive API Documentation (Swagger):** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

---

## ⚙️ Configuration & Optional LLM API Keys

DataPilot AI operates **100% offline** without third-party API dependencies. If you wish to enable optional external LLM summarization:

1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Configure optional API keys:
   - `GEMINI_API_KEY=your_gemini_key_here`
   - or `GROQ_API_KEY=your_groq_key_here`
   - or `OPENAI_API_KEY=your_openai_key_here`

---

## 👥 Author & Academic Context

- **Project:** DataPilot AI — Your All-in-One Data Analyst Workspace
- **Degree:** M.Sc. Data Science
- **Core Competencies Demonstrated:** Full-Stack Web Architecture (FastAPI + HTML/CSS/JS), Automated Data Cleaning & Imputation, Analytical DuckDB SQL, Exploratory Data Analysis, Interactive Visualizations (Plotly), Scikit-Learn Machine Learning Pipelines, and Software Testing.

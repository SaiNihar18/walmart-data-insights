# 🛒 Walmart Sales Intelligence Platform

**An end-to-end, production-grade Data Science & Engineering portfolio project** — combining a modular ETL pipeline, advanced SQL analytics, machine learning, and an interactive Streamlit web dashboard.

> Built on **10,000 Walmart sales transactions** across **100 branches**, **6 product categories**, and **5 years (2019–2023)**.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://docker.com)
[![CI](https://github.com/SaiNihar18/walmart-data-insights/actions/workflows/test.yml/badge.svg)](https://github.com/SaiNihar18/walmart-data-insights/actions)

---

## 🌐 Live Dashboard

👉 **[walmart-data-insights.streamlit.app](https://walmart-data-insights.streamlit.app)**

---

## 🗺️ Project Workflow

```
Raw Data (Kaggle CSV)
        │
        ▼
┌─────────────────────┐
│   ETL Pipeline      │  extract → transform → load
│   (run_etl.py)      │  • Remove duplicates & nulls
│   src/etl.py        │  • Parse currency strings
│   src/db.py         │  • Calculate total revenue
└──────────┬──────────┘  • Load to PostgreSQL (Docker)
           │
           ▼
┌─────────────────────┐
│  SQL Analytics      │  9 business questions solved
│  MySQL Queries.sql  │  • Window Functions (RANK)
│                     │  • CTEs, Date Arithmetic
│                     │  • YoY Revenue Analysis
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  EDA Notebook       │  Rich visual analysis
│  eda.ipynb          │  • 5-year sales trends
│                     │  • Category profit margins
│                     │  • Correlation heatmap
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ML Modeling        │  Two production models
│  (run_modeling.py)  │  • K-Means Branch Clustering
│  src/modeling.py    │  • XGBoost Sales Forecasting
└──────────┬──────────┘  → models/*.joblib
           │
           ▼
┌─────────────────────┐
│  Streamlit App      │  4-page interactive dashboard
│  app.py             │  • Executive KPI Overview
│                     │  • Sales Forecasting (2023)
│                     │  • Branch Market Segments
│                     │  • Price Elasticity Simulator
└─────────────────────┘
```

---

## 📁 Project Structure

```
Walmart_SQL_Python/
│
├── 📁 .github/workflows/
│   └── test.yml                    # CI/CD: Auto-runs pytest on every GitHub push
│
├── 📁 src/                         # Core Python package
│   ├── __init__.py
│   ├── db.py                       # Secure DB engine (env-var based, URL-encoded passwords)
│   ├── etl.py                      # Extract → Transform → Load functions with logging
│   └── modeling.py                 # K-Means clustering + XGBoost sales forecasting
│
├── 📁 tests/
│   └── test_etl.py                 # 3 pytest unit tests for data cleaning logic
│
├── 📁 models/                      # Serialized ML artifacts (auto-generated)
│   ├── branch_kmeans.joblib        # Fitted K-Means model
│   ├── branch_scaler.joblib        # Feature StandardScaler
│   ├── sales_forecaster.joblib     # Fitted XGBoost model
│   └── sales_features.joblib       # Feature column list
│
├── app.py                          # ✨ 4-page Streamlit dashboard
├── run_etl.py                      # ETL pipeline entry point
├── run_modeling.py                 # ML pipeline entry point
├── eda.ipynb                       # Exploratory Data Analysis notebook
├── MySQL Queries.sql               # 9 advanced SQL business queries
├── docker-compose.yml              # PostgreSQL + pgAdmin Docker setup
├── .env.example                    # Credentials template (never commit .env)
├── .gitignore
└── requirements.txt
```

---

## 🔧 Tech Stack

| Layer | Tools |
|---|---|
| **Language** | Python 3.10+, SQL |
| **Data Processing** | Pandas, NumPy |
| **Databases** | PostgreSQL, MySQL, SQLAlchemy |
| **Infrastructure** | Docker, Docker Compose |
| **Security** | python-dotenv (`.env` credentials) |
| **EDA & Visualization** | Matplotlib, Seaborn, Plotly |
| **Machine Learning** | Scikit-learn (K-Means), XGBoost |
| **Dashboard** | Streamlit |
| **Testing & CI/CD** | pytest, GitHub Actions |

---

## ⚙️ Local Setup Guide

### Prerequisites
- Python 3.10+, Git
- Docker & Docker Compose *(optional — only needed for live DB loading)*

### 1. Clone & Install
```bash
git clone https://github.com/SaiNihar18/walmart-data-insights.git
cd walmart-data-insights
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Spin Up the Database (Docker)
```bash
docker compose up -d
# PostgreSQL → localhost:5432
# pgAdmin UI → http://localhost:8080
```

### 4. Run ETL Pipeline
```bash
python run_etl.py
```
*Extracts 10,051 records → cleans → saves `walmart_cleaned.csv` → loads to database*

### 5. Train ML Models
```bash
python run_modeling.py
```
*Trains K-Means + XGBoost → saves model artifacts to `models/`*

### 6. Launch Dashboard
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

### 7. Run Unit Tests
```bash
python -m pytest tests/
```

---

## 📊 Dashboard Pages

| Page | Description |
|---|---|
| **📊 Executive Overview** | KPI cards (Revenue, Profit, Rating, Transactions) + Monthly trend, Payment share donut, Category bar chart — all with dynamic filters |
| **📈 Sales Forecasting** | Select any category → view XGBoost predictions vs actual 2023 weekly sales with RMSE & MAPE metrics |
| **🏷️ Market Segments** | K-Means cluster scatter plot (Revenue vs Rating), cluster profile descriptions for all 100 branches |
| **🎯 Price Elasticity Simulator** | Adjust price ±20% → instantly see projected volume and revenue change using category elasticity coefficients |

---

## 🗄️ SQL Business Queries (9 Solved)

| # | Business Question | SQL Feature |
|---|---|---|
| 1 | Payment method distribution & transaction volumes | GROUP BY, COUNT, SUM |
| 2 | Highest-rated category per branch | Window Function (RANK, PARTITION BY) |
| 3 | Busiest transaction day per branch | DAYNAME, Window Function |
| 4 | Total quantity sold by payment method | GROUP BY, SUM |
| 5 | Rating statistics per city & category | MIN, MAX, AVG |
| 6 | Total profit per product category | Derived Column, ORDER BY |
| 7 | Most common payment method per branch | CTE + RANK |
| 8 | Sales by shift (Morning/Afternoon/Evening) | CASE WHEN, HOUR |
| 9 | Top 5 branches with highest YoY revenue decline | CTE, JOIN, Arithmetic |

---

## 🤖 Machine Learning Results

### K-Means Branch Clustering
Groups 100 branches into **4 performance cohorts** using:
- Total Revenue, Avg Transaction Value, Avg Profit Margin, Avg Rating
- Normalized product category sales share (pivot table)
- Standardized with `StandardScaler` before clustering

| Cluster | Branches | Profile |
|---|---|---|
| 0 | 31 | Balanced mid-tier |
| 1 | 25 | High-satisfaction outlets |
| 2 | 17 | Premium low-volume |
| 3 | 27 | High-volume powerhouses |

### XGBoost Weekly Sales Forecasting
| Detail | Value |
|---|---|
| Features | 4 lag values, rolling mean/std, month, week number, category dummies |
| Train Period | Jan 2019 – Dec 2022 (403 weekly observations) |
| Test Period | Jan 2023 – Dec 2023 (121 weekly observations) |
| RMSE | $748.20 |
| MAPE | 73.94% (baseline — weekly category sales range $1K–$4K) |

---

## ✅ CI/CD Pipeline

Every push to `main` automatically:
1. Spins up a clean **Ubuntu** environment
2. Installs all Python dependencies
3. Runs `python -m pytest tests/` (3 unit tests)
4. Reports ✅ pass / ❌ fail on every commit

---

## 🌐 Deploying Your Own Copy

### Option A — Streamlit Community Cloud (Free, Recommended)
1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New App**
3. Select your fork, branch `main`, file `app.py`
4. Click **Deploy** — live in ~2 minutes

### Option B — Render
1. Go to [render.com](https://render.com) → New Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

---

## 📈 Key Business Insights

- **Food & Beverages** generates the highest cumulative revenue across all branches
- **Saturday** is the single busiest transaction day across all locations
- **E-wallet** is the most preferred payment method overall
- **Electronic accessories** have the highest price elasticity — small price changes cause large demand swings
- Branches in **Cluster 2** (17 branches) show premium high-rating characteristics despite lower volumes

---

## 📦 Data Source

| Property | Detail |
|---|---|
| Dataset | [Walmart 10K Sales Dataset](https://www.kaggle.com/najir0123/walmart-10k-sales-datasets) |
| Source | Kaggle — by @najir0123 |
| Raw Records | 10,051 |
| Cleaned Records | 9,969 |
| Date Span | January 2019 – December 2023 |
| Branches | 100 across 98 US cities |

---

## 🙏 Acknowledgments

- Dataset by [@najir0123](https://www.kaggle.com/najir0123) on Kaggle
- Inspired by Walmart's retail analytics and supply chain case studies

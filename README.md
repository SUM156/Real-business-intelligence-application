# 📊 Sales Analytics Dashboard

> An interactive Streamlit business intelligence dashboard — KPI cards, revenue trends, regional breakdowns, and top-product rankings from any CSV/Excel sales dataset.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Folder Structure](#-folder-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Testing](#-testing)
- [Screenshots](#-screenshots)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

Every retail and e-commerce company runs a dashboard exactly like this one — a place where a manager can glance at revenue, profit margin, and which regions/products are winning, without opening a spreadsheet. This project builds that dashboard from scratch: a clean pandas-based analytics layer, Plotly visualizations, and an interactive Streamlit UI with filters and CSV upload.

## ❓ Problem Statement

Raw sales data in a spreadsheet answers no questions by itself — someone has to pivot it, chart it, and update it every time new data arrives. This dashboard automates that entire loop: drop in a CSV, get KPIs and charts instantly, filter by date/region/category, and see everything update live.

## ✨ Features

- **5 headline KPI cards** — Total Revenue, Total Profit, Total Orders, Profit Margin %, Average Order Value.
- **Monthly revenue & profit trend** — dual-line chart showing seasonality over time.
- **Regional performance ranking** — horizontal bar chart, highest-revenue region first.
- **Revenue share by category** — donut chart.
- **Top 10 products by revenue** — horizontal bar chart.
- **Interactive sidebar filters** — date range, region, and category, all live-updating every chart and KPI.
- **CSV/Excel upload** — analyze your own dataset, not just the bundled sample.
- **Robust data validation** — missing columns, unparseable dates, and malformed numeric data are all caught with clear error messages instead of producing silently-wrong KPIs.
- **27 automated tests** covering data loading, aggregation math, and chart construction — verified end-to-end with Streamlit's official `AppTest` framework (the whole app renders with zero exceptions against the real 1000-row dataset).

## 🛠️ Technology Stack

| Layer | Technology | Why |
|---|---|---|
| UI framework | Streamlit | Turns a Python script into a full interactive web app with zero HTML/JS |
| Data processing | Pandas | Industry-standard tabular aggregation |
| Visualization | Plotly Express / Graph Objects | Interactive, hoverable charts out of the box |
| File support | openpyxl | Enables `.xlsx`/`.xls` upload, not just CSV |
| Testing | pytest + `streamlit.testing.v1.AppTest` | Unit tests for logic, integration test for the full rendered app |

## 🏗️ Architecture

```
        sales_data.csv / uploaded file
                    ↓
          data_loader.py     ← Load, validate schema, coerce types
                    ↓
          analytics.py         ← Pure aggregation: KPIs, trends, rankings
                    ↓
           charts.py              ← Plotly figure builders
                    ↓
            app.py                   ← Streamlit UI: widgets, layout, wiring
```

**Key design decision — zero Streamlit imports below the UI layer:** `data_loader.py`, `analytics.py`, and `charts.py` never import `streamlit`. Every function takes plain pandas/Python inputs and returns plain pandas/Plotly outputs. This is what makes 27 tests possible without ever launching a browser — and it's also what let me verify the ENTIRE app end-to-end with Streamlit's `AppTest` tool, since the UI layer itself stayed thin enough to be trustworthy by inspection.

## 📁 Folder Structure

```
day21_sales_dashboard/
├── app.py                    # Streamlit entry point (streamlit run app.py)
├── requirements.txt
├── README.md
├── GUIDE.txt                   # Roman Urdu setup guide
├── data/
│   └── sales_data.csv           # Bundled 1000-row sample dataset
├── src/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── data_loader.py             # CSV/Excel loading + validation
│   ├── analytics.py                 # Pure KPI/aggregation functions
│   └── charts.py                       # Plotly figure builders
└── tests/
    ├── test_data_loader.py
    ├── test_analytics.py             # Hand-verified aggregation math
    └── test_charts.py
```

## ⚙️ Installation

```bash
git clone https://github.com/<your-username>/sales-analytics-dashboard.git
cd sales-analytics-dashboard
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Usage

```bash
streamlit run app.py
```

This opens the dashboard in your browser (default: `http://localhost:8501`). It loads the bundled 1000-row sample dataset automatically — or use the sidebar file uploader to analyze your own CSV/Excel file. Required columns: `order_id, order_date, region, product, category, quantity, unit_price, revenue, cost, profit`.

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

**Result: 27/27 tests passing.** The full app was also verified with Streamlit's official `AppTest` framework — it renders all 5 KPI cards and 4 charts against the real dataset with zero exceptions.

## 📸 Screenshots

> _(Add screenshots here after running `streamlit run app.py` locally — e.g. the KPI row, the revenue trend chart, and the regional bar chart.)_

```
[ KPI Cards Row Screenshot Placeholder ]
[ Revenue Trend Chart Screenshot Placeholder ]
[ Regional Performance Chart Screenshot Placeholder ]
```

## 🗺️ Future Roadmap

- [ ] Deploy to Streamlit Community Cloud for a live public demo
- [ ] Add year-over-year comparison view
- [ ] Add forecasting (e.g. Prophet/ARIMA) for next-quarter revenue projection
- [ ] Add customer-level RFM (Recency, Frequency, Monetary) segmentation
- [ ] Export filtered view as a PDF report (reuse the reportlab pattern from Day 14)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for any new logic in `src/`
4. Ensure `pytest tests/` passes before opening a PR

## 📄 License

MIT License — free to use, modify, and distribute.
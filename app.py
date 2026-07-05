"""
app.py
======
Streamlit entry point. Run with: streamlit run app.py

This file owns ONLY UI concerns -- page layout, widgets, and wiring
user input to the pure functions in `src/`. Every number shown on
screen is computed by `src/analytics.py`; every chart is built by
`src/charts.py`. If you ever need to change how a KPI is CALCULATED,
you'll never need to touch this file.
"""

from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from src.analytics import (
    category_breakdown,
    compute_kpis,
    monthly_revenue_trend,
    regional_performance,
    top_products,
)
from src.charts import (
    build_category_pie_chart,
    build_regional_bar_chart,
    build_revenue_trend_chart,
    build_top_products_chart,
)
from src.data_loader import load_sales_data
from src.exceptions import DashboardError

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

DEFAULT_DATA_PATH = "data/sales_data.csv"

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def _load_default_dataset(path: str) -> pd.DataFrame:
    """Load the bundled sample dataset, cached across reruns.

    `st.cache_data` means the CSV is parsed from disk exactly once per
    session (not on every widget interaction) -- Streamlit reruns the
    entire script top-to-bottom on every user action, so without this
    the app would re-read and re-validate the same file dozens of
    times per minute of normal use.
    """
    return load_sales_data(path)


def _load_uploaded_dataset(uploaded_file) -> pd.DataFrame:
    """Load a user-uploaded CSV via the same validated loader path.

    Uses a temp file rather than reading `uploaded_file` directly with
    pandas, so `load_sales_data`'s file-extension dispatch logic (CSV
    vs Excel) is exercised identically to the default-dataset path --
    one code path for both sources, not two.
    """
    import tempfile
    from pathlib import Path

    suffix = Path(uploaded_file.name).suffix or ".csv"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    return load_sales_data(tmp_path)


def render_kpi_cards(dataframe: pd.DataFrame) -> None:
    """Render the top row of KPI metric cards."""
    kpis = compute_kpis(dataframe)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"${kpis.total_revenue:,.0f}")
    col2.metric("Total Profit", f"${kpis.total_profit:,.0f}")
    col3.metric("Total Orders", f"{kpis.total_orders:,}")
    col4.metric("Profit Margin", f"{kpis.profit_margin_percent:.1f}%")
    col5.metric("Avg Order Value", f"${kpis.average_order_value:,.2f}")


def render_sidebar_filters(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filter widgets and return the filtered DataFrame.

    Filtering happens here (in the UI layer) rather than in
    `analytics.py` deliberately -- "which rows the user currently
    wants to see" is a UI concern tied to widget state, whereas
    `analytics.py` should stay agnostic about wherever its input
    DataFrame came from.
    """
    st.sidebar.header("🔍 Filters")

    min_date = dataframe["order_date"].min().date()
    max_date = dataframe["order_date"].max().date()
    date_range = st.sidebar.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    all_regions = sorted(dataframe["region"].unique())
    selected_regions = st.sidebar.multiselect(
        "Region", options=all_regions, default=all_regions
    )

    all_categories = sorted(dataframe["category"].unique())
    selected_categories = st.sidebar.multiselect(
        "Category", options=all_categories, default=all_categories
    )

    filtered = dataframe[
        dataframe["region"].isin(selected_regions)
        & dataframe["category"].isin(selected_categories)
    ]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered["order_date"].dt.date >= start_date)
            & (filtered["order_date"].dt.date <= end_date)
        ]

    return filtered


def main() -> None:
    """Render the full dashboard."""
    st.title("📊 Sales Analytics Dashboard")
    st.caption("Interactive business intelligence — revenue, profit, and regional trends")

    uploaded_file = st.sidebar.file_uploader(
        "Upload your own sales CSV/Excel", type=["csv", "xlsx", "xls"]
    )

    try:
        if uploaded_file is not None:
            dataframe = _load_uploaded_dataset(uploaded_file)
            st.sidebar.success(f"Loaded {len(dataframe):,} rows from {uploaded_file.name}")
        else:
            dataframe = _load_default_dataset(DEFAULT_DATA_PATH)
            st.sidebar.info(f"Using bundled sample dataset ({len(dataframe):,} rows)")
    except DashboardError as exc:
        st.error(f"❌ Could not load sales data: {exc}")
        st.stop()
    except FileNotFoundError:
        st.error(
            f"❌ Sample dataset not found at '{DEFAULT_DATA_PATH}'. "
            "Upload a CSV/Excel file to continue."
        )
        st.stop()

    filtered_dataframe = render_sidebar_filters(dataframe)

    if filtered_dataframe.empty:
        st.warning("⚠️ No orders match the current filters.")
        st.stop()

    render_kpi_cards(filtered_dataframe)
    st.divider()

    trend_data = monthly_revenue_trend(filtered_dataframe)
    st.plotly_chart(build_revenue_trend_chart(trend_data), width='stretch')

    left_col, right_col = st.columns(2)
    with left_col:
        regional_data = regional_performance(filtered_dataframe)
        st.plotly_chart(build_regional_bar_chart(regional_data), width='stretch')
    with right_col:
        category_data = category_breakdown(filtered_dataframe)
        st.plotly_chart(build_category_pie_chart(category_data), width='stretch')

    products_data = top_products(filtered_dataframe, top_n=10)
    st.plotly_chart(build_top_products_chart(products_data), width='stretch')

    with st.expander("📋 View raw filtered data"):
        st.dataframe(filtered_dataframe, width='stretch')


if __name__ == "__main__":
    main()
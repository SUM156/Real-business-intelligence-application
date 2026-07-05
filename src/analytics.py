# Pure KPI/aggregation functions placeholder
"""
analytics.py
=============
Pure aggregation functions over a validated sales DataFrame. Nothing
in this module imports Streamlit, builds a chart, or prints anything
-- every function takes a DataFrame and returns a DataFrame, Series,
or plain number. This is what makes the entire analytics layer
testable with a 5-row hand-built DataFrame instead of clicking through
a running dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class KPISummary:
    """Headline Key Performance Indicators for a sales dataset.

    Attributes:
        total_revenue: Sum of all order revenue.
        total_profit: Sum of all order profit.
        total_orders: Number of orders.
        profit_margin_percent: total_profit / total_revenue * 100.
        average_order_value: total_revenue / total_orders.
    """

    total_revenue: float
    total_profit: float
    total_orders: int
    profit_margin_percent: float
    average_order_value: float


def compute_kpis(dataframe: pd.DataFrame) -> KPISummary:
    """Compute headline KPIs for a sales dataset.

    Args:
        dataframe: A validated sales DataFrame (see `data_loader.py`).

    Returns:
        A `KPISummary`. For an empty DataFrame, returns all-zero KPIs
        rather than raising -- an empty filtered selection (e.g. "no
        orders in this date range") is a valid dashboard state, not
        an error.
    """
    total_orders = len(dataframe)
    if total_orders == 0:
        return KPISummary(0.0, 0.0, 0, 0.0, 0.0)

    total_revenue = round(float(dataframe["revenue"].sum()), 2)
    total_profit = round(float(dataframe["profit"].sum()), 2)
    profit_margin = round(100 * total_profit / total_revenue, 2) if total_revenue else 0.0
    average_order_value = round(total_revenue / total_orders, 2)

    return KPISummary(
        total_revenue=total_revenue,
        total_profit=total_profit,
        total_orders=total_orders,
        profit_margin_percent=profit_margin,
        average_order_value=average_order_value,
    )


def monthly_revenue_trend(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue and profit by calendar month.

    Returns:
        A DataFrame with columns ['month', 'revenue', 'profit'],
        sorted chronologically. 'month' is a `Period` cast to string
        (e.g. "2025-01") so it renders cleanly on a chart x-axis
        without timezone/day-of-month noise.
    """
    if dataframe.empty:
        return pd.DataFrame(columns=["month", "revenue", "profit"])

    working = dataframe.copy()
    working["month"] = working["order_date"].dt.to_period("M").astype(str)

    grouped = (
        working.groupby("month", as_index=False)[["revenue", "profit"]]
        .sum()
        .sort_values("month")
        .reset_index(drop=True)
    )
    return grouped


def regional_performance(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue, profit, and order count by region.

    Returns:
        A DataFrame with columns ['region', 'revenue', 'profit',
        'orders'], sorted by revenue descending (highest-performing
        region first -- the natural reading order for a leaderboard).
    """
    if dataframe.empty:
        return pd.DataFrame(columns=["region", "revenue", "profit", "orders"])

    grouped = (
        dataframe.groupby("region", as_index=False)
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "count"))
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )
    return grouped


def top_products(dataframe: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Rank products by total revenue.

    Args:
        dataframe: A validated sales DataFrame.
        top_n: How many top products to return.

    Returns:
        A DataFrame with columns ['product', 'revenue', 'quantity',
        'orders'], the top `top_n` products by revenue, descending.
    """
    if dataframe.empty:
        return pd.DataFrame(columns=["product", "revenue", "quantity", "orders"])

    grouped = (
        dataframe.groupby("product", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            quantity=("quantity", "sum"),
            orders=("order_id", "count"),
        )
        .sort_values("revenue", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return grouped


def category_breakdown(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by product category -- feeds the pie/donut
    chart showing which product lines drive the business.
    """
    if dataframe.empty:
        return pd.DataFrame(columns=["category", "revenue"])

    grouped = (
        dataframe.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )
    return grouped
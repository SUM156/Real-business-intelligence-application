# Plotly figure builders placeholder
"""
charts.py
=========
Builds Plotly figures from already-aggregated DataFrames (produced by
`analytics.py`). This module knows about chart TYPES (line, bar, pie)
and STYLING -- it does not know how to aggregate data. That separation
means a chart's visual design can change (e.g. bar -> area) without
touching a single aggregation function, and vice versa.
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# A consistent color palette used across every chart in the dashboard,
# so the visual identity feels designed rather than default-Plotly.
COLOR_SEQUENCE = px.colors.qualitative.Set2


def build_revenue_trend_chart(monthly_data: pd.DataFrame) -> go.Figure:
    """Build a dual-line chart of monthly revenue and profit over time.

    Args:
        monthly_data: Output of `analytics.monthly_revenue_trend`.

    Returns:
        A Plotly `Figure` with two lines (revenue, profit) sharing an
        x-axis of month labels.
    """
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=monthly_data["month"],
            y=monthly_data["revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(color="#2E86AB", width=3),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=monthly_data["month"],
            y=monthly_data["profit"],
            mode="lines+markers",
            name="Profit",
            line=dict(color="#4CAF50", width=3),
        )
    )
    figure.update_layout(
        title="Monthly Revenue & Profit Trend",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        hovermode="x unified",
        template="plotly_white",
    )
    return figure


def build_regional_bar_chart(regional_data: pd.DataFrame) -> go.Figure:
    """Build a horizontal bar chart ranking regions by revenue.

    Horizontal orientation (rather than vertical) is used deliberately
    -- region names are text labels, and horizontal bars let long
    labels render fully without rotating or truncating axis text.
    """
    figure = px.bar(
        regional_data,
        x="revenue",
        y="region",
        orientation="h",
        color="region",
        color_discrete_sequence=COLOR_SEQUENCE,
        text="revenue",
        title="Revenue by Region",
    )
    figure.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    figure.update_layout(
        showlegend=False,
        xaxis_title="Revenue ($)",
        yaxis_title="",
        template="plotly_white",
        yaxis=dict(categoryorder="total ascending"),
    )
    return figure


def build_top_products_chart(products_data: pd.DataFrame) -> go.Figure:
    """Build a horizontal bar chart of the top products by revenue."""
    figure = px.bar(
        products_data,
        x="revenue",
        y="product",
        orientation="h",
        color="revenue",
        color_continuous_scale="Blues",
        text="revenue",
        title="Top Products by Revenue",
    )
    figure.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    figure.update_layout(
        xaxis_title="Revenue ($)",
        yaxis_title="",
        template="plotly_white",
        yaxis=dict(categoryorder="total ascending"),
        coloraxis_showscale=False,
    )
    return figure


def build_category_pie_chart(category_data: pd.DataFrame) -> go.Figure:
    """Build a donut chart showing revenue share by product category."""
    figure = px.pie(
        category_data,
        names="category",
        values="revenue",
        hole=0.45,
        color_discrete_sequence=COLOR_SEQUENCE,
        title="Revenue Share by Category",
    )
    figure.update_traces(textposition="inside", textinfo="percent+label")
    figure.update_layout(template="plotly_white")
    return figure
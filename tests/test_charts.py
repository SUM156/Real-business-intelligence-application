"""Unit tests for src/charts.py -- Plotly figure construction.

These tests don't (and can't meaningfully) assert on pixel-level
rendering. Instead they verify the CONTRACT each builder must satisfy:
returns a real `go.Figure`, contains the expected number of data
traces, and doesn't blow up on realistic aggregated input.
"""

import pandas as pd
import plotly.graph_objects as go

from src.charts import (
    build_category_pie_chart,
    build_regional_bar_chart,
    build_revenue_trend_chart,
    build_top_products_chart,
)


def test_revenue_trend_chart_returns_figure():
    monthly_data = pd.DataFrame(
        {"month": ["2025-01", "2025-02"], "revenue": [100.0, 200.0], "profit": [40.0, 80.0]}
    )
    figure = build_revenue_trend_chart(monthly_data)
    assert isinstance(figure, go.Figure)


def test_revenue_trend_chart_has_two_lines():
    """Must plot revenue AND profit as separate traces, not just one."""
    monthly_data = pd.DataFrame(
        {"month": ["2025-01"], "revenue": [100.0], "profit": [40.0]}
    )
    figure = build_revenue_trend_chart(monthly_data)
    assert len(figure.data) == 2


def test_regional_bar_chart_returns_figure():
    regional_data = pd.DataFrame(
        {"region": ["North", "South"], "revenue": [500.0, 300.0], "profit": [200.0, 100.0], "orders": [10, 5]}
    )
    figure = build_regional_bar_chart(regional_data)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) > 0


def test_top_products_chart_returns_figure():
    products_data = pd.DataFrame(
        {"product": ["Widget", "Gadget"], "revenue": [500.0, 300.0], "quantity": [50, 30], "orders": [20, 15]}
    )
    figure = build_top_products_chart(products_data)
    assert isinstance(figure, go.Figure)


def test_category_pie_chart_returns_figure():
    category_data = pd.DataFrame({"category": ["Tools", "Electronics"], "revenue": [300.0, 700.0]})
    figure = build_category_pie_chart(category_data)
    assert isinstance(figure, go.Figure)
    assert figure.data[0].type == "pie"


def test_category_pie_chart_is_a_donut():
    """The chart should have a hole (donut style), not a plain pie --
    verifies the styling contract, not just "a pie chart exists".
    """
    category_data = pd.DataFrame({"category": ["Tools"], "revenue": [100.0]})
    figure = build_category_pie_chart(category_data)
    assert figure.data[0].hole > 0
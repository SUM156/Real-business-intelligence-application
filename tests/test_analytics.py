"""Unit tests for src/analytics.py -- pure aggregation logic."""

import pandas as pd
import pytest

from src.analytics import (
    category_breakdown,
    compute_kpis,
    monthly_revenue_trend,
    regional_performance,
    top_products,
)


@pytest.fixture
def sample_dataframe():
    """A small, hand-built dataset with known, easy-to-verify totals."""
    return pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "order_date": pd.to_datetime(
                ["2025-01-05", "2025-01-20", "2025-02-10", "2025-02-15"]
            ),
            "region": ["North", "South", "North", "East"],
            "product": ["Widget", "Gadget", "Widget", "Gizmo"],
            "category": ["Tools", "Tools", "Tools", "Electronics"],
            "quantity": [2, 1, 3, 1],
            "unit_price": [10.0, 5.0, 10.0, 40.0],
            "revenue": [20.0, 5.0, 30.0, 40.0],
            "cost": [12.0, 3.0, 18.0, 24.0],
            "profit": [8.0, 2.0, 12.0, 16.0],
        }
    )


def test_compute_kpis_on_empty_dataframe_returns_zeros():
    kpis = compute_kpis(pd.DataFrame())
    assert kpis.total_revenue == 0.0
    assert kpis.total_orders == 0
    assert kpis.profit_margin_percent == 0.0


def test_compute_kpis_totals(sample_dataframe):
    kpis = compute_kpis(sample_dataframe)
    assert kpis.total_revenue == 95.0  # 20+5+30+40
    assert kpis.total_profit == 38.0  # 8+2+12+16
    assert kpis.total_orders == 4


def test_compute_kpis_profit_margin(sample_dataframe):
    kpis = compute_kpis(sample_dataframe)
    # 38 / 95 * 100 = 40.0
    assert kpis.profit_margin_percent == 40.0


def test_compute_kpis_average_order_value(sample_dataframe):
    kpis = compute_kpis(sample_dataframe)
    # 95 / 4 = 23.75
    assert kpis.average_order_value == 23.75


def test_monthly_revenue_trend_groups_by_month(sample_dataframe):
    trend = monthly_revenue_trend(sample_dataframe)
    assert list(trend["month"]) == ["2025-01", "2025-02"]
    assert trend.loc[trend["month"] == "2025-01", "revenue"].iloc[0] == 25.0  # 20+5
    assert trend.loc[trend["month"] == "2025-02", "revenue"].iloc[0] == 70.0  # 30+40


def test_monthly_revenue_trend_on_empty_dataframe():
    result = monthly_revenue_trend(pd.DataFrame(columns=["order_date", "revenue", "profit"]))
    assert result.empty
    assert list(result.columns) == ["month", "revenue", "profit"]


def test_regional_performance_aggregates_correctly(sample_dataframe):
    regional = regional_performance(sample_dataframe)
    north_row = regional[regional["region"] == "North"].iloc[0]
    assert north_row["revenue"] == 50.0  # 20+30
    assert north_row["orders"] == 2


def test_regional_performance_sorted_by_revenue_descending(sample_dataframe):
    regional = regional_performance(sample_dataframe)
    revenues = list(regional["revenue"])
    assert revenues == sorted(revenues, reverse=True)


def test_top_products_ranks_by_revenue(sample_dataframe):
    products = top_products(sample_dataframe, top_n=10)
    assert products.iloc[0]["product"] == "Widget"  # 20+30 = 50, highest
    assert products.iloc[0]["revenue"] == 50.0


def test_top_products_respects_top_n_limit(sample_dataframe):
    products = top_products(sample_dataframe, top_n=2)
    assert len(products) == 2


def test_category_breakdown_aggregates_by_category(sample_dataframe):
    categories = category_breakdown(sample_dataframe)
    tools_row = categories[categories["category"] == "Tools"].iloc[0]
    assert tools_row["revenue"] == 55.0  # 20+5+30


def test_category_breakdown_on_empty_dataframe():
    result = category_breakdown(pd.DataFrame(columns=["category", "revenue"]))
    assert result.empty
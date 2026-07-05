"""Unit tests for src/data_loader.py -- CSV loading and schema validation."""

import pandas as pd
import pytest

from src.data_loader import load_sales_data
from src.exceptions import InvalidSalesDataError

VALID_CSV_HEADER = (
    "order_id,order_date,region,product,category,quantity,"
    "unit_price,revenue,cost,profit\n"
)


def _write_csv(tmp_path, content: str, filename: str = "sales.csv"):
    file_path = tmp_path / filename
    file_path.write_text(content)
    return str(file_path)


def test_load_valid_csv(tmp_path):
    content = VALID_CSV_HEADER + "1,2025-01-01,North,Widget,Tools,2,10.0,20.0,12.0,8.0\n"
    path = _write_csv(tmp_path, content)

    dataframe = load_sales_data(path)

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["region"] == "North"
    assert pd.api.types.is_datetime64_any_dtype(dataframe["order_date"])


def test_load_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales_data(str(tmp_path / "does_not_exist.csv"))


def test_load_missing_column_raises(tmp_path):
    content = "order_id,order_date,region\n1,2025-01-01,North\n"
    path = _write_csv(tmp_path, content)

    with pytest.raises(InvalidSalesDataError):
        load_sales_data(path)


def test_load_empty_file_raises(tmp_path):
    path = _write_csv(tmp_path, VALID_CSV_HEADER)
    with pytest.raises(InvalidSalesDataError):
        load_sales_data(path)


def test_load_unsupported_extension_raises(tmp_path):
    path = _write_csv(tmp_path, "not real data", filename="sales.txt")
    with pytest.raises(InvalidSalesDataError):
        load_sales_data(path)


def test_load_unparseable_dates_raises(tmp_path):
    content = VALID_CSV_HEADER + "1,not-a-date,North,Widget,Tools,2,10.0,20.0,12.0,8.0\n"
    path = _write_csv(tmp_path, content)

    with pytest.raises(InvalidSalesDataError):
        load_sales_data(path)


def test_load_mostly_bad_numeric_column_raises(tmp_path):
    """If more than half of a numeric column is garbage, treat it as a
    malformed file rather than silently coercing everything to NaN.
    """
    rows = [VALID_CSV_HEADER]
    for i in range(10):
        revenue = "not-a-number" if i < 6 else "20.0"
        rows.append(f"{i},2025-01-01,North,Widget,Tools,2,10.0,{revenue},12.0,8.0\n")
    path = _write_csv(tmp_path, "".join(rows))

    with pytest.raises(InvalidSalesDataError):
        load_sales_data(path)


def test_load_drops_rows_with_bad_dates_but_keeps_good_ones(tmp_path):
    content = (
        VALID_CSV_HEADER
        + "1,2025-01-01,North,Widget,Tools,2,10.0,20.0,12.0,8.0\n"
        + "2,not-a-date,South,Gadget,Tools,1,5.0,5.0,3.0,2.0\n"
    )
    path = _write_csv(tmp_path, content)

    dataframe = load_sales_data(path)
    assert len(dataframe) == 1
    assert dataframe.iloc[0]["order_id"] == 1


def test_numeric_columns_coerced_to_numeric_dtype(tmp_path):
    content = VALID_CSV_HEADER + "1,2025-01-01,North,Widget,Tools,2,10.0,20.0,12.0,8.0\n"
    path = _write_csv(tmp_path, content)

    dataframe = load_sales_data(path)
    for column in ["quantity", "unit_price", "revenue", "cost", "profit"]:
        assert pd.api.types.is_numeric_dtype(dataframe[column])
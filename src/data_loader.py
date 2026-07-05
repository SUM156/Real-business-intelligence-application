"""
data_loader.py
===============
Loads sales data from a CSV or Excel file into a validated pandas
DataFrame. This is the ONLY module that touches raw file I/O or does
schema validation -- every other module assumes it's already been
handed a clean, correctly-typed DataFrame.

Why validate here instead of letting bad data flow downstream?
A dashboard is exactly the wrong place to discover a silent data bug
-- a missing column should fail loudly and immediately with a clear
message, not produce a KPI card that quietly shows "$0.00" because a
groupby on a missing column returned nothing.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

import pandas as pd

from src.exceptions import InvalidSalesDataError

logger = logging.getLogger(__name__)

# Every valid sales dataset MUST contain these columns. This is the
# single source of truth for the schema -- if the dataset format ever
# changes, this is the only line that needs updating.
REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "region",
    "product",
    "category",
    "quantity",
    "unit_price",
    "revenue",
    "cost",
    "profit",
}

NUMERIC_COLUMNS = ["quantity", "unit_price", "revenue", "cost", "profit"]


def load_sales_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load and validate a sales dataset from CSV or Excel.

    Args:
        file_path: Path to a `.csv`, `.xlsx`, or `.xls` file.

    Returns:
        A validated DataFrame with `order_date` parsed as a real
        datetime column and all numeric columns coerced to numbers.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        InvalidSalesDataError: If required columns are missing, if
            `order_date` can't be parsed, or if numeric columns
            contain non-numeric garbage that can't be coerced.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Sales data file not found: {file_path}")

    if path.suffix.lower() == ".csv":
        dataframe = pd.read_csv(path)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        dataframe = pd.read_excel(path)
    else:
        raise InvalidSalesDataError(
            f"Unsupported file type '{path.suffix}'. Use .csv, .xlsx, or .xls."
        )

    _validate_schema(dataframe)
    dataframe = _clean_and_coerce(dataframe)

    logger.info("Loaded %d sales records from %s", len(dataframe), path)
    return dataframe


def _validate_schema(dataframe: pd.DataFrame) -> None:
    """Ensure every required column is present.

    Raises:
        InvalidSalesDataError: If any required column is missing.
    """
    missing = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing:
        raise InvalidSalesDataError(
            f"Sales data is missing required column(s): {sorted(missing)}. "
            f"Expected columns: {sorted(REQUIRED_COLUMNS)}."
        )

    if dataframe.empty:
        raise InvalidSalesDataError("Sales data file contains no rows.")


def _clean_and_coerce(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Parse dates and coerce numeric columns to proper dtypes.

    Uses `.copy()` before mutating so the caller's original DataFrame
    reference (if they kept one) is never silently mutated as a side
    effect -- a classic pandas footgun this function deliberately avoids.

    Raises:
        InvalidSalesDataError: If `order_date` can't be parsed, or if
            a numeric column is more than half unparseable (a strong
            signal the file is malformed rather than just having a
            handful of dirty rows).
    """
    dataframe = dataframe.copy()

    parsed_dates = pd.to_datetime(dataframe["order_date"], errors="coerce")
    if parsed_dates.isna().all():
        raise InvalidSalesDataError(
            "Could not parse any values in 'order_date' as dates."
        )
    dataframe["order_date"] = parsed_dates

    for column in NUMERIC_COLUMNS:
        coerced = pd.to_numeric(dataframe[column], errors="coerce")
        bad_fraction = coerced.isna().mean()
        if bad_fraction > 0.5:
            raise InvalidSalesDataError(
                f"Column '{column}' contains mostly non-numeric values "
                f"({bad_fraction:.0%} unparseable)."
            )
        dataframe[column] = coerced

    # Drop rows where date parsing failed outright (a handful of bad
    # rows shouldn't crash the whole dashboard -- but they also
    # shouldn't silently corrupt aggregations with NaT).
    before_count = len(dataframe)
    dataframe = dataframe.dropna(subset=["order_date"])
    dropped = before_count - len(dataframe)
    if dropped:
        logger.warning("Dropped %d row(s) with unparseable order_date", dropped)

    return dataframe
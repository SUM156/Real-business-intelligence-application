"""
exceptions.py
=============
Custom exception hierarchy for the dashboard's data layer.
"""


class DashboardError(Exception):
    """Base class for every error raised by this application."""


class InvalidSalesDataError(DashboardError):
    """Raised when a CSV/Excel file is missing required columns or
    contains data that fails basic sanity checks (e.g. negative
    revenue, unparseable dates).
    """
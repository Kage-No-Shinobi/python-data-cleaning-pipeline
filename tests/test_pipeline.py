import pandas as pd
import pytest

from pipeline import clean_frame


def sample_frame():
    return pd.DataFrame([
        {"Transaction ID": "A1", "Date": "2026-01-02", "Description": " Taxi ", "Type": "Expense", "Amount": "₦1,250.00", "Currency": "NGN", "Category": "Transport"},
        {"Transaction ID": "A1", "Date": "2026-01-02", "Description": "Taxi", "Type": "Expense", "Amount": "₦1,250.00", "Currency": "NGN", "Category": "Transport"},
        {"Transaction ID": "A2", "Date": "not-a-date", "Description": "Item", "Type": "Expense", "Amount": "₦500.00", "Currency": "NGN", "Category": "Food"},
        {"Transaction ID": "A3", "Date": "03/01/2026", "Description": "", "Type": "Income", "Amount": "₦2,000.00", "Currency": "NGN", "Category": ""},
        {"Transaction ID": "A4", "Date": "2026-01-04", "Description": "Refund", "Type": "Income", "Amount": "₦0.00", "Currency": "NGN", "Category": "Sales"},
    ])


def test_pipeline_standardizes_rows_and_reports_changes():
    cleaned, report = clean_frame(sample_frame())
    assert len(cleaned) == 2
    assert cleaned.loc[0, "amount"] == 1250.00
    assert cleaned.loc[1, "date"] == "2026-01-03"
    assert cleaned.loc[1, "category"] == "Uncategorized"
    assert cleaned.loc[1, "description"] == "No description"
    assert report["duplicate_ids_removed"] == 1
    assert report["invalid_date_rows_removed"] == 1
    assert report["non_positive_amount_rows_removed"] == 1
    assert report["rows_output"] == 2


def test_pipeline_rejects_missing_required_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        clean_frame(pd.DataFrame([{"transaction_id": "x", "amount": "3"}]))


def test_pipeline_rejects_empty_input():
    with pytest.raises(ValueError, match="no rows"):
        clean_frame(pd.DataFrame(columns=["transaction_id", "date", "description", "type", "amount", "currency", "category"]))

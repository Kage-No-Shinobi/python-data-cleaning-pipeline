"""Clean a transaction CSV and write an auditable summary."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {"transaction_id", "date", "description", "type", "amount", "currency", "category"}


def _parse_date(value: Any) -> pd.Timestamp:
    if pd.isna(value) or not str(value).strip():
        return pd.NaT
    text = str(value).strip()
    formats = ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%b %d, %Y")
    for date_format in formats:
        try:
            return pd.Timestamp(datetime.strptime(text, date_format).date())
        except ValueError:
            continue
    return pd.NaT


def _parse_amount(value: Any) -> float:
    if pd.isna(value):
        return float("nan")
    text = str(value).strip().replace("₦", "").replace(",", "").replace("NGN", "").strip()
    try:
        return float(text)
    except ValueError:
        return float("nan")


def clean_frame(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return a cleaned copy and counts describing each transformation."""
    if raw.empty:
        raise ValueError("input CSV has no rows")

    frame = raw.copy()
    frame.columns = [
        re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower()).strip("_")
        for column in frame.columns
    ]
    missing_columns = REQUIRED_COLUMNS - set(frame.columns)
    if missing_columns:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing_columns))}")

    rows_input = len(frame)
    for column in ("transaction_id", "description", "type", "currency", "category"):
        frame[column] = frame[column].astype("string").str.strip()
        frame[column] = frame[column].replace("", pd.NA)

    frame["date"] = frame["date"].map(_parse_date)
    frame["amount"] = frame["amount"].map(_parse_amount)
    frame["type"] = frame["type"].str.lower().replace(
        {"credit": "income", "deposit": "income", "inflow": "income", "debit": "expense", "withdrawal": "expense", "outflow": "expense"}
    )

    missing_id = frame["transaction_id"].isna()
    invalid_date = frame["date"].isna()
    invalid_amount = frame["amount"].isna()
    non_positive_amount = frame["amount"].notna() & (frame["amount"] <= 0)
    invalid_type = ~frame["type"].isin(["income", "expense"])
    invalid_rows = missing_id | invalid_date | invalid_amount | non_positive_amount | invalid_type

    categories_filled = int(frame["category"].isna().sum())
    descriptions_filled = int(frame["description"].isna().sum())
    frame["category"] = frame["category"].fillna("Uncategorized")
    frame["description"] = frame["description"].fillna("No description")

    valid = frame.loc[~invalid_rows].copy()
    duplicate_mask = valid.duplicated(subset=["transaction_id"], keep="first")
    duplicate_ids_removed = int(duplicate_mask.sum())
    cleaned = valid.loc[~duplicate_mask].copy()
    cleaned["date"] = cleaned["date"].dt.strftime("%Y-%m-%d")
    cleaned["amount"] = cleaned["amount"].round(2)
    cleaned = cleaned[["transaction_id", "date", "description", "type", "amount", "currency", "category"]]
    cleaned = cleaned.sort_values(["date", "transaction_id"], kind="stable").reset_index(drop=True)

    report = {
        "rows_input": rows_input,
        "duplicate_ids_removed": duplicate_ids_removed,
        "missing_id_rows_removed": int(missing_id.sum()),
        "invalid_date_rows_removed": int(invalid_date.sum()),
        "invalid_amount_rows_removed": int(invalid_amount.sum()),
        "non_positive_amount_rows_removed": int(non_positive_amount.sum()),
        "invalid_type_rows_removed": int(invalid_type.sum()),
        "invalid_rows_removed": int(invalid_rows.sum()),
        "categories_filled": categories_filled,
        "descriptions_filled": descriptions_filled,
        "rows_output": len(cleaned),
    }
    return cleaned, report


def run_pipeline(input_path: Path, output_path: Path, report_path: Path) -> dict[str, Any]:
    raw = pd.read_csv(input_path, dtype="string", keep_default_na=True)
    cleaned, report = clean_frame(raw)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = run_pipeline(args.input, args.output, args.report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

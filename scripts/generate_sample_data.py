"""Generate a deterministic, intentionally messy synthetic CSV."""

from __future__ import annotations

import csv
from pathlib import Path


def build_rows() -> list[dict[str, str]]:
    rows = []
    categories = ["Transport", "Food", "Utilities", "Supplies", "Sales"]
    for index in range(1, 117):
        month = (index % 4) + 1
        day = (index % 28) + 1
        date_iso = f"2026-{month:02d}-{day:02d}"
        date_value = date_iso if index % 3 == 0 else (
            f"{day:02d}/{month:02d}/2026" if index % 3 == 1 else f"{('Jan','Feb','Mar','Apr')[month-1]} {day:02d}, 2026"
        )
        amount = ((index * 375) % 87500) + 250
        kind = "Income" if index % 7 == 0 else "Expense"
        row = {
            "Transaction ID": f"TX-{index:04d}",
            "Date": date_value,
            "Description": f"Sample {kind.lower()} item {index}",
            "Type": kind,
            "Amount": f"₦{amount:,.2f}",
            "Currency": "NGN",
            "Category": categories[index % len(categories)],
        }
        rows.append(row)

    for index in (10, 70, 80):
        if index == 10:
            rows[index - 1]["Amount"] = ""
        elif index == 70:
            rows[index - 1]["Date"] = "not-a-date"
        else:
            rows[index - 1]["Amount"] = "₦0.00"
    for index in (8, 33, 77, 98):
        rows[index - 1]["Category"] = ""
    for index in (12, 81):
        rows[index - 1]["Description"] = ""

    # Four extra records intentionally repeat an existing transaction ID.
    for index in (4, 24, 64, 94):
        rows.append(rows[index - 1].copy())
    return rows


def main() -> None:
    destination = Path(__file__).resolve().parents[1] / "data" / "raw" / "transactions_messy.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} synthetic rows at {destination}")


if __name__ == "__main__":
    main()

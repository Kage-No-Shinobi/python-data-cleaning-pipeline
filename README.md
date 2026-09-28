# Python Data Cleaning Pipeline

A reproducible Pandas workflow that turns a deliberately messy, synthetic transaction CSV into a typed, deduplicated dataset and a machine-readable cleaning report.

## Results from the included sample

The generator creates **120 raw rows**. The pipeline removes duplicate transaction IDs and invalid rows, fills missing descriptive fields, and writes a cleaned CSV plus a JSON report. The checked-in sample should produce 113 cleaned rows; the report is the source of truth for all counts.

The dataset is synthetic and contains no real customer or financial records. The amounts are illustrative NGN values.

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/generate_sample_data.py
python src/pipeline.py \
  --input data/raw/transactions_messy.csv \
  --output data/processed/transactions_clean.csv \
  --report reports/cleaning_report.json
```

## Cleaning steps

1. Standardize column names and trim text fields.
2. Parse mixed date formats and currency-formatted amounts.
3. Normalize transaction types to `income` or `expense`.
4. Remove rows with invalid dates, invalid or non-positive amounts, and duplicate transaction IDs.
5. Fill missing descriptions and categories with explicit labels.
6. Sort the output and write a JSON report of every change.

The pipeline does not silently impute dates or amounts. Rows missing a usable date or amount are excluded and counted in the report.

## Notebook

Open `notebooks/cleaning_walkthrough.ipynb` after installing the requirements. It walks through loading the raw data, calling the same pipeline function, and inspecting the report and cleaned table.

## Tests

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=src python -m pytest
```

## Resume-ready description

Built a Pandas pipeline that processes 120 raw synthetic rows into a validated cleaned dataset, removes duplicate and invalid transactions, standardizes dates and amounts, and exports an auditable JSON report.

# Data Cleaning Demo

A pandas-based data cleaning demo. Takes a deliberately "dirty" CSV (simulated e-commerce order records) and cleans it into a consistent, usable dataset.

## Dirty data issues handled

| Issue | Example |
|-------|---------|
| Missing values | empty cell, `N/A`, `unknown` |
| Duplicate rows | full duplicates |
| Mixed date formats | `2024-03-15` / `03/28/2024` / `29.03.2024` |
| Mixed currency formats | `$1,234.56` / `1.234,56` / `1234.56` |
| Inconsistent case & whitespace | `  rick fan  ` / `RICK.FAN@EXAMPLE.COM` |
| Anomalous values | negative price, absurd price |
| Swapped fields | email in name column |

## Requirements

```
pip install pandas
```

## Usage

```bash
python generate_dirty_data.py   # create dirty sample data (data/dirty_orders.csv)
python clean_orders.py          # clean it (data/cleaned_orders.csv + cleaning_report.txt)
```

## Output

- `data/cleaned_orders.csv` — clean dataset (UTF-8 with BOM)
- `data/cleaning_report.txt` — before/after summary

## Cleaning steps

1. Deduplicate by row
2. Fix swapped fields
3. Fill / mark missing values
4. Normalize dates → `YYYY-MM-DD`
5. Normalize amounts → float (handles US & European formats)
6. Normalize strings (strip, lower-case)
7. Filter anomalous values

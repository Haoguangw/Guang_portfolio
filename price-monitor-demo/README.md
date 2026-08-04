# Price Monitor Demo

A small, production-shaped **price monitoring** script: scrapes product prices on a schedule, stores history, and reports what changed since the last run.

## What it demonstrates

- **Scraping** — extracts titles + prices from books.toscrape.com (official practice site)
- **History** — every run appends to `data/price_history.csv`
- **Change detection** — compares current prices with last known values and reports:
  - new products / removed products
  - price rises / price drops (with before → after)
- **Delivery hook** — `notify()` stub where email / Google Sheets / Telegram would plug in

## Usage

```bash
python price_monitor.py run --limit 20            # real run
python price_monitor.py run --limit 20 --simulate-change   # test mode: simulate price moves to demo change detection
```

## How this becomes a client product

1. Schedule it: **GitHub Actions cron** (free, client zero-maintenance) or Windows Task Scheduler
2. Point `notify()` at the client's channel (email / Google Sheets via gspread / Telegram bot)
3. Client opens a live spreadsheet — prices auto-update every run, changes flagged

## Note

`--simulate-change` is a **test-only flag** (the practice site's prices are static); the change-detection logic itself runs identically on real data.

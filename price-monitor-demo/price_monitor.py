#!/usr/bin/env python3
"""
Price Monitor Demo
==================
A small, production-shaped price monitor: scrapes prices on a schedule,
stores history, and reports what changed since the last run.

Target: books.toscrape.com (official practice site - safe to scrape).

How a real client deployment works:
  - Run this script on a schedule (GitHub Actions cron, or Windows Task Scheduler)
  - Each run: scrape -> compare with history -> report changes
  - Changes can be emailed / written to Google Sheets (see notify stub)

Usage:
  python price_monitor.py run [--limit N] [--simulate-change]
"""

import argparse
import csv
import os
import random
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "price_history.csv")
HEADERS = {"User-Agent": "PriceMonitorDemo/1.0 (+contact: demo@example.com)"}

FIELDS = ["timestamp", "title", "price", "url"]


def scrape_books(limit: int = 100) -> list[dict]:
    """Scrape book titles + prices from the catalogue (first page, paginated up to limit)."""
    books = []
    page = 1
    while len(books) < limit:
        url = f"{BASE_URL}catalogue/page-{page}.html" if page > 1 else BASE_URL
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article.product_pod")
        if not articles:
            break
        for a in articles:
            title = a.select_one("h3 a")["title"].strip()
            price = a.select_one("p.price_color").get_text(strip=True)
            rel = a.select_one("h3 a")["href"]
            full = BASE_URL + rel.replace("../", "catalogue/")
            books.append({"title": title, "price": price, "url": full})
            if len(books) >= limit:
                break
        page += 1
        time.sleep(1)  # polite delay
    return books


def load_history() -> dict[str, dict]:
    """Load latest known price per product, keyed by title."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    latest: dict[str, dict] = {}
    with open(HISTORY_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            latest[row["title"]] = row  # later rows overwrite -> keeps last seen
    return latest


def append_history(books: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_file = not os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for b in books:
            writer.writerow({"timestamp": ts, **b})


def parse_price(p: str) -> float:
    m = re.search(r"\d+(?:\.\d+)?", p.replace(",", ""))
    return float(m.group(0)) if m else 0.0


def diff_report(books: list[dict], prev: dict[str, dict], simulate: bool) -> str:
    """Compare current scrape with history; return a human-readable change report."""
    cur = {b["title"]: b for b in books}
    prev_keys = set(prev.keys())
    cur_keys = set(cur.keys())

    new = cur_keys - prev_keys                       # never seen before
    removed = prev_keys - cur_keys                   # no longer listed
    risen = dropped = 0
    details = []

    for title in cur_keys & prev_keys:
        if simulate and random.random() < 0.25:
            # test-only: simulate a price move so the change detection is visible
            p_new = parse_price(cur[title]["price"]) * random.uniform(0.85, 1.15)
            shown = f"${p_new:.2f}"
        else:
            shown = cur[title]["price"]
        p_prev = parse_price(prev[title]["price"])
        p_cur = parse_price(shown)
        if p_cur > p_prev:
            risen += 1
            details.append(f"  ^ {title}: {prev[title]['price']} -> {shown}")
        elif p_cur < p_prev:
            dropped += 1
            details.append(f"  v {title}: {prev[title]['price']} -> {shown}")

    lines = [
        "=" * 60,
        f"PRICE MONITOR REPORT  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "=" * 60,
        f"Scraped      : {len(books)} products",
        f"New products : {len(new)}",
        f"Removed      : {len(removed)}",
        f"Price risen  : {risen}",
        f"Price dropped: {dropped}",
        "Changes:",
    ]
    lines += details if details else ["  (no price changes)"]
    if simulate:
        lines.append("NOTE: --simulate-change active (test mode, prices shown are simulated).")
    return "\n".join(lines)


def notify(report: str) -> None:
    """Stub for delivery: email / Google Sheets / Telegram hook lives here in production."""
    # In production: send report via SMTP, gspread write, or Telegram bot API.
    pass


def write_html_report(books: list[dict], report: str, out_path: str = "report.html") -> str:
    """Write a self-contained HTML report the client can open in any browser."""
    rows = []
    for b in books[:100]:
        rows.append(
            f"<tr><td>{b['title']}</td><td>{b['price']}</td>"
            f"<td><a href='{b['url']}'>link</a></td></tr>"
        )
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Price Monitor Report</title>
<style>
body{{font-family:Arial,sans-serif;background:#f5f7fa;margin:40px;color:#1f3864}}
pre{{background:#fff;border:1px solid #d8e0ee;border-radius:8px;padding:16px;white-space:pre-wrap}}
table{{border-collapse:collapse;width:100%;background:#fff;border:1px solid #d8e0ee}}
th,td{{border:1px solid #d8e0ee;padding:8px 12px;text-align:left;font-size:14px}}
th{{background:#eef4fc}}
h1{{font-size:22px}}
</style></head><body>
<h1>Price Monitor Report</h1>
<pre>{report}</pre>
<h2>Latest snapshot</h2>
<table><tr><th>Title</th><th>Price</th><th>Link</th></tr>{''.join(rows)}</table>
</body></html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def write_to_sheets(books: list[dict], credentials_file: str, sheet_name: str) -> None:
    """Write the latest snapshot into a Google Sheet (production mode).

    Requires: pip install gspread google-auth
    credentials_file: path to service-account JSON (created in Google Cloud Console)
    sheet_name: name of the target sheet (share it with the service account email)
    """
    import gspread
    from google.oauth2 import service_account

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_file(credentials_file, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    rows = [[b["title"], b["price"], b["url"]] for b in books]
    sheet.clear()
    sheet.append_rows([[ "title", "price", "url" ]] + rows)
    print(f"Written {len(rows)} rows to Google Sheets: {sheet_name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run", help="run a monitoring pass")
    ap.add_argument("--limit", type=int, default=50, help="max products to scrape")
    ap.add_argument("--simulate-change", action="store_true",
                    help="test mode: simulate random price moves to demo change detection")
    ap.add_argument("--html", action="store_true",
                    help="also write a self-contained HTML report")
    ap.add_argument("--sheet-credentials", type=str, default=None,
                    help="path to Google service-account JSON for Sheets delivery")
    ap.add_argument("--sheet-name", type=str, default="PriceMonitor",
                    help="Google Sheet name to write to (with --sheet-credentials)")
    args = ap.parse_args()

    try:
        books = scrape_books(args.limit)
    except Exception as e:  # noqa: BLE001
        print(f"SCRAPE FAILED: {e}")
        return 1

    prev = load_history()
    report = diff_report(books, prev, args.simulate_change)
    print(report)
    append_history(books)
    notify(report)
    if args.html:
        out = write_html_report(books, report)
        print(f"HTML report written -> {out}")
    if args.sheet_credentials:
        write_to_sheets(books, args.sheet_credentials, args.sheet_name)
    print(f"\nHistory appended -> {HISTORY_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

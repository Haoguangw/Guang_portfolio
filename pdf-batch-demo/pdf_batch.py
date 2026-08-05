#!/usr/bin/env python3
"""
PDF Batch Processor Demo
========================
One command turns a folder of messy PDFs into a clean Excel summary
plus a re-organized archive folder.

What it does per PDF:
  1. Extract invoice number, date, billed-to company, line items, total
  2. Append a row to summary.xlsx
  3. Rename + copy the file into archive/<company>_<date>_<invno>.pdf
  4. Print a human-readable processing report

Usage:
  python pdf_batch.py process [--input invoices] [--output output]

A real client deployment would add: OCR for scanned PDFs, email of the
summary, and watch-folder automation (new PDF dropped -> auto processed).
"""

import argparse
import os
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pdfplumber
from openpyxl import Workbook

BASE = os.path.dirname(os.path.abspath(__file__))


def extract_invoice(path: str) -> dict | None:
    """Extract key fields from one invoice PDF. Returns None if unreadable."""
    with pdfplumber.open(path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)

    def grab(pattern, flags=0):
        m = re.search(pattern, text, flags)
        return m.group(1).strip() if m else None

    inv_no = grab(r"Invoice #:\s*([A-Z0-9\-]+)", re.IGNORECASE)
    date = grab(r"Date:\s*(\d{4}-\d{2}-\d{2})")
    company = grab(r"Billed to:\s*(.+)")
    # totals: last occurrence of TOTAL: $x.xx
    totals = re.findall(r"TOTAL:\s*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    total = totals[-1] if totals else None
    # line items: rows between header and Subtotal
    lines = []
    for m in re.finditer(r"^([A-Za-z][A-Za-z ()]+?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)$",
                         text, re.MULTILINE):
        lines.append((m.group(1).strip(), int(m.group(2)),
                      float(m.group(3)), float(m.group(4))))

    if not (inv_no and date and company and total):
        return None
    return {"file": os.path.basename(path), "invoice_no": inv_no,
            "date": date, "company": company, "total": float(total.replace(",", "")),
            "line_items": len(lines)}


def process(input_dir: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    archive = os.path.join(output_dir, "archive")
    os.makedirs(archive, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Invoices"
    ws.append(["Source File", "Invoice #", "Date", "Company", "Total ($)", "Line Items"])

    ok, failed = 0, []
    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(input_dir, fname)
        data = extract_invoice(path)
        if data is None:
            failed.append(fname)
            print(f"[FAIL] {fname} - could not extract fields")
            continue
        ws.append([data["file"], data["invoice_no"], data["date"],
                   data["company"], data["total"], data["line_items"]])
        safe_company = re.sub(r"[^\w\-]+", "_", data["company"])
        new_name = f"{safe_company}_{data['date']}_{data['invoice_no']}.pdf"
        shutil.copy2(path, os.path.join(archive, new_name))
        print(f"[OK]   {fname} -> {new_name}  (${data['total']:.2f})")
        ok += 1

    xlsx = os.path.join(output_dir, "summary.xlsx")
    wb.save(xlsx)

    print("\n" + "=" * 56)
    print(f"PROCESSED: {ok} PDFs  |  FAILED: {len(failed)}")
    print(f"Excel summary -> {xlsx}")
    print(f"Archive       -> {archive}")
    if failed:
        print("Failed files:", ", ".join(failed))
    print("=" * 56)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("process", help="run the batch process")
    ap.add_argument("--input", default=os.path.join(BASE, "invoices"),
                    help="folder with PDFs to process")
    ap.add_argument("--output", default=os.path.join(BASE, "output"),
                    help="folder for summary + archive")
    args = ap.parse_args()
    process(args.input, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

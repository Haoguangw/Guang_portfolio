#!/usr/bin/env python3
"""
Generate sample invoice PDFs for the pdf-batch-demo.

Creates 10 realistic-looking invoices with varying customers, dates,
amounts and invoice numbers - including a few edge cases (missing tax
line, different layouts) so the batch tool has something interesting to handle.
"""
import os
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "invoices")
os.makedirs(OUT_DIR, exist_ok=True)

COMPANIES = ["Northwind Trading", "Blue Oak LLC", "Summit Solutions",
             "Harbor Freight Co", "Cedar & Pine Ltd", "Iron Bridge Inc",
             "Maple Grove Foods", "Redstone Partners", "Silver Creek Media",
             "Golden Gate Imports"]
ITEMS = [("Web scraping service", 450), ("Data cleaning", 280),
         ("API integration", 600), ("Monthly monitoring", 120),
         ("Consulting (hourly)", 95), ("Report automation", 340),
         ("Batch processing", 200), ("Setup fee", 150)]


def draw_invoice(path, company, inv_no, date, lines, tax_rate):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    # header
    c.setFillColorRGB(0.12, 0.22, 0.39)
    c.rect(0, h - 40 * mm, w, 40 * mm, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20 * mm, h - 25 * mm, "INVOICE")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, h - 33 * mm, f"Invoice #: {inv_no}")
    c.drawString(120 * mm, h - 25 * mm, f"Date: {date}")
    # company
    c.setFillColorRGB(0.2, 0.25, 0.35)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, h - 55 * mm, f"Billed to: {company}")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, h - 61 * mm, "123 Business Ave, Suite 400")
    c.drawString(20 * mm, h - 65 * mm, "Springfield, USA")
    # line items
    y = h - 85 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Description")
    c.drawString(120 * mm, y, "Qty")
    c.drawString(150 * mm, y, "Unit $")
    c.drawString(180 * mm, y, "Total $")
    c.line(20 * mm, y - 4 * mm, w - 20 * mm, y - 4 * mm)
    y -= 10 * mm
    subtotal = 0
    c.setFont("Helvetica", 10)
    for name, price in lines:
        qty = random.randint(1, 4)
        total = price * qty
        subtotal += total
        c.drawString(20 * mm, y, name)
        c.drawString(120 * mm, y, str(qty))
        c.drawString(150 * mm, y, f"{price:.2f}")
        c.drawString(180 * mm, y, f"{total:.2f}")
        y -= 7 * mm
    # totals
    y -= 8 * mm
    tax = subtotal * tax_rate
    c.setFont("Helvetica-Bold", 10)
    c.drawString(150 * mm, y, "Subtotal:")
    c.drawString(180 * mm, y, f"{subtotal:.2f}")
    y -= 7 * mm
    c.drawString(150 * mm, y, "Tax:")
    c.drawString(180 * mm, y, f"{tax:.2f}")
    y -= 9 * mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(150 * mm, y, "TOTAL:")
    c.drawString(180 * mm, y, f"{subtotal + tax:.2f}")
    c.save()


def main():
    random.seed(42)
    start = datetime(2026, 6, 1)
    for i in range(10):
        company = COMPANIES[i]
        inv_no = f"INV-2026-{1000 + i * 37}"
        date = (start + timedelta(days=i * 9)).strftime("%Y-%m-%d")
        n_lines = random.randint(1, 3)
        lines = random.sample(ITEMS, n_lines)
        tax_rate = 0.0 if i == 7 else 0.08  # one invoice has no tax line
        path = os.path.join(OUT_DIR, f"invoice_{company.replace(' ', '_')}_{date}.pdf")
        draw_invoice(path, company, inv_no, date, lines, tax_rate)
        print(f"generated {os.path.basename(path)}")
    print("done -", len(os.listdir(OUT_DIR)), "invoices in", OUT_DIR)


if __name__ == "__main__":
    main()

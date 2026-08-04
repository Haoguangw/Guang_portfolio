# -*- coding: utf-8 -*-
"""生成三个项目的作品集 PDF（英文，客户视角）"""
import csv
from fpdf import FPDF

# ---------- 数据准备 ----------
# 爬虫输出样例
with open(r"D:\code\portfolio\web-scraper-demo\output\books.csv", encoding="utf-8-sig") as f:
    books = list(csv.DictReader(f))[:6]

# 数据清洗样例
with open(r"D:\code\portfolio\data-cleaning-demo\data\cleaned_orders.csv", encoding="utf-8-sig") as f:
    orders = list(csv.DictReader(f))[:5]
with open(r"D:\code\portfolio\data-cleaning-demo\data\dirty_orders.csv", encoding="utf-8-sig") as f:
    dirty = list(csv.DictReader(f))[:3]

# ---------- PDF 工具 ----------
class PortfolioPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(150)
        self.cell(0, 6, "Haoguang Wang - Portfolio", align="R")
        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def section_title(self, txt):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 40, 80)
        self.multi_cell(0, 7, txt)
        self.ln(1)

    def body(self, txt):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(40)
        self.multi_cell(0, 5.5, txt)
        self.ln(2)

    def label(self, txt):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(20, 40, 80)
        self.cell(0, 6, txt)
        self.ln(6)

    def table(self, headers, rows):
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(30, 60, 110)
        self.set_text_color(255)
        # 列宽
        w = [0] * len(headers)
        avail = self.w - 2 * self.l_margin
        for i, h in enumerate(headers):
            w[i] = avail / len(headers)
        for i, h in enumerate(headers):
            self.cell(w[i], 6, h[:18], border=1, fill=True)
        self.ln()
        fill = False
        for r in rows:
            if fill:
                self.set_fill_color(232, 238, 248)  # 浅灰蓝，不用深色
            for i, c in enumerate(r):
                self.set_font("Helvetica", "", 8)
                self.set_text_color(30)
                self.cell(w[i], 5.5, str(c)[:18], border=1, fill=fill)
            self.ln()
            fill = not fill
        self.ln(3)

def new_pdf():
    pdf = PortfolioPDF()
    pdf.set_margins(14, 14, 14)
    pdf.add_page()
    return pdf

# ---------- 项目 1：Web Scraper ----------
pdf = new_pdf()
pdf.section_title("Web Scraper - Book Data Collection to CSV")
pdf.label("Overview")
pdf.body(
    "Built a polite, production-style web scraper that collects book listings from "
    "books.toscrape.com (an official scraping practice site) and exports them to a clean CSV file.\n\n"
    "Key features:\n"
    "- Pagination handling across multiple pages\n"
    "- Rate limiting (2-3s random delays) to be respectful to the server\n"
    "- Character encoding fix (handles the pound sign correctly)\n"
    "- Clean CSV output with UTF-8 BOM (opens directly in Excel)\n\n"
    "Safety practices: respects robots.txt, limited page count, custom User-Agent."
)
pdf.label("Sample Output (60 records collected)")
pdf.table(
    ["title", "price", "rating", "availability"],
    [[b["title"][:22], b["price"], b["rating"], b["availability"][:10]] for b in books]
)
pdf.label("Tech Stack")
pdf.body("Python 3, requests, BeautifulSoup4, CSV")
pdf.output(r"C:\Users\29480\Desktop\portfolio_1_web_scraper.pdf")
print("1 done")

# ---------- 项目 2：Data Cleaning ----------
pdf = new_pdf()
pdf.section_title("Data Cleaning with Pandas - Dirty to Clean CSV")
pdf.label("Overview")
pdf.body(
    "A data-cleaning project that turns a deliberately messy e-commerce dataset into a "
    "consistent, production-ready spreadsheet.\n\n"
    "Problems handled:\n"
    "- Missing values (empty cells, 'N/A', 'unknown')\n"
    "- Duplicate rows\n"
    "- Mixed date formats (2024-03-15 / 03/28/2024 / 29.03.2024)\n"
    "- Mixed currency formats ($1,234.56 vs 1.234,56 - US vs European)\n"
    "- Inconsistent casing and whitespace\n"
    "- Anomalous values (negative/absurd prices)\n"
    "- Swapped fields (email in name column)\n\n"
    "Result: 24 dirty rows -> 19 clean rows, with a before/after report documenting every change."
)
pdf.label("Before (dirty data)")
pdf.table(["order_id", "order_date", "customer_name", "amount"],
          [[d["order_id"], d["order_date"][:12], d["customer_name"][:16], str(d["amount"])[:10]] for d in dirty])
pdf.label("After (cleaned data)")
pdf.table(["order_id", "order_date", "customer_name", "amount"],
          [[o["order_id"], o["order_date"][:12], o["customer_name"][:16], str(o["amount"])[:10]] for o in orders])
pdf.label("Tech Stack")
pdf.body("Python 3, pandas, CSV, data validation")
pdf.output(r"C:\Users\29480\Desktop\portfolio_2_data_cleaning.pdf")
print("2 done")

# ---------- 项目 3：FFmpeg Batch ----------
pdf = new_pdf()
pdf.section_title("FFmpeg Batch Processing Tool")
pdf.label("Overview")
pdf.body(
    "A Python CLI tool that wraps FFmpeg for batch video processing, with three practical modes:\n\n"
    "1. Compress / transcode - batch compress videos to H.264 MP4 with CRF quality control\n"
    "2. Extract frames - batch extract frames at a given rate (thumbnails, stills)\n"
    "3. Extract audio - batch rip audio tracks to MP3\n\n"
    "Auto-detects FFmpeg, supports mp4/mov/avi/mkv/webm, tested on sample videos. "
    "Designed for real-world repetitive media workflows."
)
pdf.label("Sample Run")
pdf.body(
    "$ python batch_ffmpeg.py compress ./sample ./output --crf 28\n"
    "$ python batch_ffmpeg.py frames ./sample ./output --fps 1\n"
    "$ python batch_ffmpeg.py audio ./sample ./output\n\n"
    "Output: compressed MP4s, JPG frame sequences, MP3 audio files - verified on 2 test videos."
)
pdf.label("Tech Stack")
pdf.body("Python 3, FFmpeg, subprocess, CLI design")
pdf.output(r"C:\Users\29480\Desktop\portfolio_3_ffmpeg_batch.pdf")
print("3 done")

print("全部完成")

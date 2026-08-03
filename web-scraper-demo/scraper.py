#!/usr/bin/env python3
"""
Web Scraper Demo - books.toscrape.com
=====================================
一个礼貌、安全的爬虫示例：抓取前 3 页书籍列表（书名/价格/评分/库存），输出 CSV。

安全策略：
- 目标站为官方爬虫练习站（books.toscrape.com），无登录、无验证码、无隐私数据
- 遵守 robots.txt（该站无 robots.txt，默认允许，仍保持克制）
- 请求间隔 2-3 秒（限速，不给服务器压力）
- 限制页数（默认 3 页，共约 60 本书）
- 携带合理 User-Agent 标识

用法：
    python scraper.py [页数]

输出：
    output/books.csv
"""

import csv
import random
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
USER_AGENT = "PortfolioScraper/1.0 (+https://gitee.com/wang-ergoulll/guang_portfolio)"
DEFAULT_PAGES = 3
OUTPUT_FILE = "output/books.csv"


def fetch_page(page_num: int) -> str | None:
    """抓取单页 HTML，失败返回 None。"""
    url = BASE_URL.format(page_num)
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"  # 页面虽声明 latin-1，但实际为 UTF-8（£ 符号验证）
        return resp.text
    except requests.RequestException as e:
        print(f"  [第{page_num}页] 请求失败: {e}")
        return None


def parse_books(html: str) -> list[dict]:
    """从 HTML 中解析书籍列表。"""
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for article in soup.select("article.product_pod"):
        title = article.h3.a.get("title", "").strip()
        price = article.select_one("p.price_color").text.strip()
        rating = article.select_one("p.star-rating").get("class")[1]
        availability = article.select_one("p.instock.availability").text.strip()
        books.append(
            {
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
            }
        )
    return books


def main():
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PAGES
    pages = max(1, min(pages, 5))  # 硬性上限 5 页，防止误跑过多

    print(f"开始爬取前 {pages} 页 (books.toscrape.com)")
    all_books = []
    for page_num in range(1, pages + 1):
        print(f"  抓取第 {page_num} 页 ...")
        html = fetch_page(page_num)
        if html:
            books = parse_books(html)
            all_books.extend(books)
            print(f"    解析到 {len(books)} 本书")
        # 限速：随机 2-3 秒，礼貌爬取
        if page_num < pages:
            time.sleep(random.uniform(2, 3))

    if not all_books:
        print("未抓取到任何数据，退出。")
        sys.exit(1)

    # 写 CSV（UTF-8 with BOM，Excel 直接打开不乱码）
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "rating", "availability"])
        writer.writeheader()
        writer.writerows(all_books)

    print(f"\n完成！共 {len(all_books)} 本书，已保存到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

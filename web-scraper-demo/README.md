# Web Scraper Demo

A polite, safe web scraper demo that collects book listings (title / price / rating / availability) from [books.toscrape.com](https://books.toscrape.com) — an official practice site built for learning web scraping.

## Why this site

- Official scraping practice site, no login, no CAPTCHA, no private data
- Safe & legal to scrape, commonly used in tutorials

## Safety practices

- Respects `robots.txt` (this site has none, but we stay conservative anyway)
- Rate-limited: random 2-3s delay between requests
- Page limit: 3 pages by default (hard cap 5), ~60 books total
- Custom User-Agent identifies the scraper

## Requirements

```
pip install requests beautifulsoup4
```

## Usage

```bash
python scraper.py          # default: 3 pages
python scraper.py 5        # up to 5 pages
```

## Output

`output/books.csv` — UTF-8 with BOM (opens cleanly in Excel)

## Sample output

| title | price | rating | availability |
|-------|-------|--------|--------------|
| A Light in the Attic | £51.77 | Three | In stock |
| Tipping the Velvet | £53.74 | One | In stock |
| Soumission | £50.10 | One | In stock |

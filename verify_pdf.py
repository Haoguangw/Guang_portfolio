# 验证 PDF 内容
from pypdf import PdfReader

names = [
    "portfolio_1_web_scraper.pdf",
    "portfolio_2_data_cleaning.pdf",
    "portfolio_3_ffmpeg_batch.pdf",
]
for name in names:
    path = r"C:\Users\29480\Desktop" + "\\" + name
    r = PdfReader(path)
    t = r.pages[0].extract_text()
    print("===", name, "|", len(r.pages), "pages ===")
    print(t[:300].replace("\n", " | "))
    print()

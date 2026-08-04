# PDF -> PNG 高清渲染（作品集图片）
import fitz  # PyMuPDF

names = [
    "portfolio_1_web_scraper.pdf",
    "portfolio_2_data_cleaning.pdf",
    "portfolio_3_ffmpeg_batch.pdf",
]

for name in names:
    src = r"C:\Users\29480\Desktop" + "\\" + name
    out = src.replace(".pdf", ".png")
    doc = fitz.open(src)
    page = doc[0]
    # 2x 缩放渲染，高清
    mat = fitz.Matrix(2.5, 2.5)
    pix = page.get_pixmap(matrix=mat)
    pix.save(out)
    print(f"{name} -> {out}  ({pix.width}x{pix.height})")
    doc.close()
print("完成")

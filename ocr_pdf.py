# ocr_engine.py
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np

ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')

def is_text_based(page) -> bool:
    return len(page.get_text().strip()) > 30

def ocr_scanned_page(page) -> str:
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes))
    np_img = np.array(image)
    result = ocr_engine.predict(np_img, cls=True)

    lines = []
    for block in result:
        for item in block:
            lines.append(item[1][0])  # Extract recognized text
    return '\n'.join(lines)

def extract_text_from_pdf(pdf_bytes: bytes) -> list:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        try:
            if is_text_based(page):
                text = page.get_text()
            else:
                text = ocr_scanned_page(page)
        except Exception as e:
            text = f"[ERROR on page {i+1}]: {str(e)}"
        pages.append(text)
    return pages

# pdf_processor.py
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np
from typing import Dict, Any, List

class PDFProcessor:
    def __init__(self, text_threshold: int = 30):
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')
        self.text_threshold = text_threshold
        print("PaddleOCR engine loaded.")

    def _is_page_scanned(self, page: fitz.Page) -> bool:
        return len(page.get_text().strip()) < self.text_threshold

    def _convert_paddle_bbox(self, paddle_bbox: List[List[float]]) -> List[float]:
        # represent paddle ocr's 4point rectangle into two points(x,y)
        valid_points = [p for p in paddle_bbox if isinstance(p, (list, tuple)) and len(p) == 2]
        if not valid_points:
            return [0, 0, 0, 0] 
        
        x_coords = [p[0] for p in valid_points]
        y_coords = [p[1] for p in valid_points]
        
        return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

    def _process_digital_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        blocks = []
        text_blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
        for block in text_blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    blocks.append({
                        "type": "text",
                        "text": " ".join([span['text'] for span in line['spans']]),
                        "bbox": list(line['bbox'])
                    })

        image_info = page.get_images(full=True)
        for img_instance in image_info:
            xref = img_instance[0]
            bbox = page.get_image_bbox(img_instance) 
            if bbox: 
                blocks.append({
                    "type": "image",
                    "bbox": list(bbox), # convert the bbox object to a list of coordinates
                    "xref": xref
                })
        return blocks

    def _process_scanned_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        blocks = []
        pix = page.get_pixmap(dpi=150)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        np_img = np.array(image)

        ocr_result = self.ocr_engine.ocr(np_img)

        if ocr_result and ocr_result[0] is not None:
            for line in ocr_result[0]:
                if isinstance(line, list) and len(line) == 2:
                    bbox_4_point = line[0]
                    text_info = line[1]
                    if isinstance(bbox_4_point, list) and isinstance(text_info, tuple) and len(text_info) > 0:
                        text = text_info[0]
                        blocks.append({
                            "type": "text",
                            "text": text,
                            "bbox": self._convert_paddle_bbox(bbox_4_point)
                        })
        return blocks

    def process(self, pdf_bytes: bytes) -> Dict[str, Any]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        output = {
            "source_file": "from_bytes",
            "page_count": doc.page_count,
            "pages": []
        }

        for i, page in enumerate(doc):
            page_num = i + 1
            print(f"processing Page {page_num}/{doc.page_count}...")
            
            page_data = {
                "page_number": page_num,
                "page_size": [page.rect.width, page.rect.height],
                "dimensions": list(page.rect),
                "blocks": []
            }
            
            if self._is_page_scanned(page):
                page_data["blocks"] = self._process_scanned_page(page)
            else:
                page_data["blocks"] = self._process_digital_page(page)
            
            output["pages"].append(page_data)
        
        doc.close()
        print("PDF processing complete")
        return output

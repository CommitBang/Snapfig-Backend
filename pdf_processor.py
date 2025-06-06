# pdf_processor.py
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np
from typing import Dict, Any, List

class PDFProcessor:
    """
    Intelligently processes a PDF by detecting whether pages are digital or scanned
    and returns a rich, structured JSON with bounding boxes for all content.
    """
    def __init__(self, text_threshold: int = 30):
        print("Initializing PDFProcessor with PaddleOCR engine...")
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        self.text_threshold = text_threshold
        print("PaddleOCR engine loaded.")

    def _is_page_scanned(self, page: fitz.Page) -> bool:
        """Determines if a page is likely scanned."""
        return len(page.get_text().strip()) < self.text_threshold

    def _convert_paddle_bbox(self, paddle_bbox: List[List[float]]) -> List[float]:
        """Converts PaddleOCR's 4-point polygon bbox to a 2-point rectangle [x0, y0, x1, y1]."""
        x_coords = [p[0] for p in paddle_bbox]
        y_coords = [p[1] for p in paddle_bbox]
        return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

    def _process_digital_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extracts content from a digital page using direct, accurate methods."""
        blocks = []
        # Get all text blocks with precise coordinates from PyMuPDF
        text_blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
        for block in text_blocks:
            if block['type'] == 0:  # Text block
                for line in block['lines']:
                    # Add entire line as a single block for simplicity
                    blocks.append({
                        "type": "text",
                        "text": " ".join([span['text'] for span in line['spans']]),
                        "bbox": list(line['bbox'])
                    })

        # Get all image blocks with their coordinates and unique ID (xref)
        image_info = page.get_images(full=True)
        for img in image_info:
            xref = img[0]
            # get_image_bboxes can return multiple bounding boxes for the same image
            bbox_list = page.get_image_bboxes(img)
            if bbox_list:
                blocks.append({
                    "type": "image",
                    "bbox": list(bbox_list[0]),
                    "xref": xref  # This ID is needed by the gateway to extract the image
                })
        return blocks

    def _process_scanned_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extracts content from a scanned page by performing OCR with PaddleOCR."""
        blocks = []
        # Render page to a high-res image and convert to numpy array for Paddle
        pix = page.get_pixmap(dpi=200) # 200 DPI is a good balance of speed and accuracy
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        np_img = np.array(image)

        # The result from paddle is a list of lists, one for each detected text line
        ocr_result = self.ocr_engine.ocr(np_img, cls=True)

        if ocr_result and ocr_result[0] is not None:
            for line in ocr_result[0]:
                # line format: [bbox, (text, confidence)]
                bbox_4_point = line[0]
                text = line[1][0]
                # confidence = line[1][1]

                # Convert bbox and add to our standardized block list
                blocks.append({
                    "type": "text",
                    "text": text,
                    "bbox": self._convert_paddle_bbox(bbox_4_point)
                })
        return blocks

    def process(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Main entry point to process an entire PDF and return structured JSON."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        output = {
            "source_file": "from_bytes",
            "page_count": doc.page_count,
            "pages": []
        }

        for i, page in enumerate(doc):
            page_num = i + 1
            print(f"Processing Page {page_num}/{doc.page_count}...")
            
            page_data = {
                "page_number": page_num,
                "dimensions": list(page.rect),
                "blocks": []
            }
            
            if self._is_page_scanned(page):
                page_data["blocks"] = self._process_scanned_page(page)
            else:
                page_data["blocks"] = self._process_digital_page(page)
            
            output["pages"].append(page_data)
        
        doc.close()
        print("PDF processing complete.")
        return output
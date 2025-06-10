# text_processing/preprocessor.py
import re
from typing import List, Dict, Any

class TextPreprocessor:
    def clean_text(self, text: str) -> str:
        text = re.sub(r'-\n', '', text)
        text = re.sub(r'\s*\n\s*', '\n', text).strip()

        # text = re.sub(r'[^\x00-\x7F]+', ' ', text) m
        return text

    # transforms the raw OCR JSON into a standardized structure for the application.
    def preprocess(self, raw_ocr_json: Dict[str, Any]) -> Dict[str, Any]:
        processed_data = {
            "page_count": raw_ocr_json.get("page_count", 0),
            "page_dimensions": {},
            "pages": {}
        }
        
        for page_data in raw_ocr_json.get("pages", []):
            page_num_str = str(page_data.get("page_number"))
            processed_data["page_dimensions"][page_num_str] = page_data.get("dimensions", [])
            
            page_content = []
            # Process text blocks
            for block in page_data.get("blocks", []):
                if block.get("type") == "text":  # detected text block
                    cleaned_text = self.clean_text(block.get("text", ""))
                    if cleaned_text: # only add non-empty blocks
                        page_content.append({
                            "type": "text",
                            "text": cleaned_text,
                            "bbox": block.get("bbox")
                        })
                elif block.get("type") == "image":  # detected figure block
                    page_content.append({
                        "type": "image",
                        "bbox": block.get("bbox"),
                        "xref": block.get("xref") 
                    })
            
            processed_data["pages"][page_num_str] = page_content
            
        return processed_data
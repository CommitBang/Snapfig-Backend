# services/ocr_service.py
from typing import Dict, Any
import requests
from flask import current_app

class OCRService:
    def __init__(self):
        # Get the service URL from the application configuration for better flexibility
        self.ocr_url = current_app.config.get("OCR_SERVICE_URL")
        if not self.ocr_url:
            raise ValueError("OCR_SERVICE_URL not configured in the application.")

    # returns a dictionary containing the structured OCR data from the service.
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        current_app.logger.info(f"Sending PDF to OCR service at {self.ocr_url}")
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(self.ocr_url, files=files, timeout=300) # 5 min timeout
            response.raise_for_status()  
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"OCR service request failed: {e}")
            raise Exception(f"OCR service failed: {e}") from e
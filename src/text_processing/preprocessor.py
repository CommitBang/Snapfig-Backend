# preprocessor.py
import re
from typing import List, Dict
from text_processing.paragraph import ParagraphSummarizer
import requests

class TextPreprocessor:
    def __init__(self):
        self.summarizer = ParagraphSummarizer()  # initialize summarizer

    # text cleaning 
    def clean_text(self, text: str) -> str:
        text = re.sub(r'-\n', '', text)             # whitespace removal 
        text = re.sub(r'\n+', '\n\n', text)         # double spacing for each paragraph
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # non-ascii removal
        return text.strip()

    def extract_paragraphs(self, text: str) -> List[str]:
        cleaned = self.clean_text(text)
        return self.summarizer.split_into_paragraphs(cleaned)

    def summarize_paragraphs(self, paragraphs: List[str]) -> List[str]:
        return self.summarizer.summarize_paragraphs(paragraphs)

    def preprocess_and_summarize(self, page_text: str) -> Dict:
        paragraphs = self.extract_paragraphs(page_text)
        summaries = self.summarize_paragraphs(paragraphs)
        return {  # may need to connect to annotations.
            "paragraphs": paragraphs,
            "summaries": summaries
        }
    
    def preprocess(self, text_json : dict):
        return 

    def extract_json_via_ocr_server(self, pdf_path):
        ocr_url = "http://localhost:5001/ocr"  # or ngrok url
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(ocr_url, files=files)
        
        if response.status_code == 200:
            return response.json() 
        else:
            raise Exception(f"OCR failed: {response.text}")


from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json

@dataclass
class Paragraph:
    text: str
    page: int

@dataclass
class Summary:
    text: str
    page: int

class OCRDocument:
    def __init__(self, paragraphs: List[Paragraph], summaries: List[Summary]):
        self.paragraphs = paragraphs
        self.summaries = summaries

    @classmethod
    def from_json(cls, json_path: str) -> 'OCRDocument':
        """
        JSON 파일에서 paragraphs와 summaries를 객체화합니다.

        Args:
            json_path (str): JSON 파일 경로.

        Returns:
            OCRDocument: 객체화된 paragraphs와 summaries를 포함한 문서.
        """
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
            
            paragraphs = []
            summaries = []

            for page_data in data:
                page_number = page_data.get("page", -1)
                
                # 객체화된 Paragraph 생성
                for paragraph_text in page_data.get("paragraphs", []):
                    paragraphs.append(Paragraph(text=paragraph_text, page=page_number))
                
                # 객체화된 Summary 생성
                for summary_text in page_data.get("summaries", []):
                    summaries.append(Summary(text=summary_text, page=page_number))
            
            return cls(paragraphs=paragraphs, summaries=summaries)
        except Exception as e:
            print(f"JSON 파일 처리 중 오류 발생: {e}")
            return cls(paragraphs=[], summaries=[])

    def get_paragraphs(self) -> List[Paragraph]:
        return self.paragraphs

    def get_summaries(self) -> List[Summary]:
        return self.summaries

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json

@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

@dataclass
class TextRegion:
    text: str
    confidence: float
    bbox: BoundingBox
    type: Optional[str] = None
    cls_id: Optional[int] = None

@dataclass
class AlgorithmRegion(TextRegion):
    """알고리즘 영역을 나타내는 클래스"""
    def __init__(self, text: str, confidence: float, bbox: BoundingBox, cls_id: Optional[int] = None):
        super().__init__(text, confidence, bbox, "algorithm", cls_id)

@dataclass
class FormulaRegion(TextRegion):
    """수식 영역을 나타내는 클래스"""
    def __init__(self, text: str, confidence: float, bbox: BoundingBox, cls_id: Optional[int] = None):
        super().__init__(text, confidence, bbox, "formula", cls_id)

@dataclass
class FigureTitleRegion(TextRegion):
    """그림 제목 영역을 나타내는 클래스"""
    def __init__(self, text: str, confidence: float, bbox: BoundingBox, cls_id: Optional[int] = None):
        super().__init__(text, confidence, bbox, "figure_title", cls_id)

@dataclass
class ParagraphTitleRegion(TextRegion):
    """단락 제목 영역을 나타내는 클래스"""
    def __init__(self, text: str, confidence: float, bbox: BoundingBox, cls_id: Optional[int] = None):
        super().__init__(text, confidence, bbox, "paragraph_title", cls_id)

@dataclass
class HeaderRegion(TextRegion):
    """헤더 영역을 나타내는 클래스"""
    def __init__(self, text: str, confidence: float, bbox: BoundingBox, cls_id: Optional[int] = None):
        super().__init__(text, confidence, bbox, "header", cls_id)

@dataclass
class NumberRegion(TextRegion):
    """숫자 영역을 나타내는 클래스"""
    def __init__(self, text: str, confidence: float, bbox: BoundingBox, cls_id: Optional[int] = None):
        super().__init__(text, confidence, bbox, "number", cls_id)

class OCRResult:
    def __init__(self):
        self.regions: List[TextRegion] = []
        self._type_to_class = {
            "algorithm": AlgorithmRegion,
            "formula": FormulaRegion,
            "figure_title": FigureTitleRegion,
            "paragraph_title": ParagraphTitleRegion,
            "header": HeaderRegion,
            "number": NumberRegion,
            "text": TextRegion
        }

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'OCRResult':
        result = cls()
        
        # PaddleOCR의 레이아웃 분석 결과를 파싱
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
            
        # layout_det_res에서 boxes 정보 추출
        layout_boxes = json_data.get('layout_det_res', {}).get('boxes', [])
        
        # parsing_res_list에서 텍스트 내용 매핑
        text_content_map = {
            (box['block_bbox'][0], box['block_bbox'][1], box['block_bbox'][2], box['block_bbox'][3]): box['block_content']
            for box in json_data.get('parsing_res_list', [])
        }
            
        for box in layout_boxes:
            bbox = BoundingBox(
                x1=box['coordinate'][0],
                y1=box['coordinate'][1],
                x2=box['coordinate'][2],
                y2=box['coordinate'][3]
            )
            
            # 해당 좌표에 맞는 텍스트 내용 찾기
            text_content = ""
            for (x1, y1, x2, y2), content in text_content_map.items():
                if (abs(bbox.x1 - x1) < 1 and abs(bbox.y1 - y1) < 1 and 
                    abs(bbox.x2 - x2) < 1 and abs(bbox.y2 - y2) < 1):
                    text_content = content
                    break
            
            # 타입에 맞는 클래스로 객체 생성
            region_class = result._type_to_class.get(box['label'], TextRegion)
            text_region = region_class(
                text=text_content,
                confidence=box['score'],
                bbox=bbox,
                cls_id=box['cls_id']
            )
            
            result.regions.append(text_region)
            
        return result

    def to_json(self) -> Dict[str, Any]:
        return {
            'regions': [
                {
                    'text': region.text,
                    'confidence': region.confidence,
                    'bbox': [
                        region.bbox.x1,
                        region.bbox.y1,
                        region.bbox.x2,
                        region.bbox.y2
                    ],
                    'type': region.type,
                    'cls_id': region.cls_id
                }
                for region in self.regions
            ]
        }

    def get_regions_by_type(self, type_name: str) -> List[TextRegion]:
        return [region for region in self.regions if region.type == type_name]

    def get_regions_by_confidence(self, min_confidence: float) -> List[TextRegion]:
        return [region for region in self.regions if region.confidence >= min_confidence]

    # 타입별 영역을 가져오는 편의 메서드들
    def get_algorithms(self) -> List[AlgorithmRegion]:
        return [r for r in self.regions if isinstance(r, AlgorithmRegion)]

    def get_formulas(self) -> List[FormulaRegion]:
        return [r for r in self.regions if isinstance(r, FormulaRegion)]

    def get_figure_titles(self) -> List[FigureTitleRegion]:
        return [r for r in self.regions if isinstance(r, FigureTitleRegion)]

    def get_paragraph_titles(self) -> List[ParagraphTitleRegion]:
        return [r for r in self.regions if isinstance(r, ParagraphTitleRegion)]

    def get_headers(self) -> List[HeaderRegion]:
        return [r for r in self.regions if isinstance(r, HeaderRegion)]

    def get_numbers(self) -> List[NumberRegion]:
        return [r for r in self.regions if isinstance(r, NumberRegion)] 
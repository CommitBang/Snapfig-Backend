# Backend/src/objects/text_object.py
from dataclasses import dataclass, asdict
from typing import List, Union

@dataclass
class BoundingBox:  # without this, unable to create 'clickable' text
    x0: float
    y0: float
    x1: float
    y1: float

@dataclass
class InteractiveElement:
    page_num: int
    reference_bbox: BoundingBox

    def to_dict(self):
        # converts the dataclass to a dictionary for JSON serialization
        return asdict(self)

@dataclass
class AnnotationLink(InteractiveElement):
    # page_num is inherited
    target_text: str                          
    some_optional_field: str = "default_value" 
    
@dataclass
class FigureLink(InteractiveElement):
    target_xref: int  
    pdf_filename: str
    element_type: str = "figure" 

@dataclass
class UncaptionedImage(InteractiveElement):
    # page_num and reference_bbox are inherited from InteractiveElement.
    # to_dict() method is also inherited.
    xref: int
    pdf_filename: str
    element_type: str = "uncaptioned_image"


# just for type specification
InteractiveElementList = List[Union[AnnotationLink, FigureLink, UncaptionedImage]]
# meaning InteractiveElement list comprises set of annotationlink object or figurelink object or uncaptionedimage object
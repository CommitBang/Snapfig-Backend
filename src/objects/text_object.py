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
    # link from annotation to full text
    element_type: str = "annotation"
    target_text: str  # full text part which will show up on user's click

@dataclass
class FigureLink(InteractiveElement):
    # link from figure reference to actual figure
    element_type: str = "figure"
    target_xref: int  # id of figure
    pdf_filename: str  #filename needed to make the summarization API call.

# just for type specification
InteractiveElementList = List[Union[AnnotationLink, FigureLink]]
# meaning InteractiveElement list comprises set of either annotationlink object or figurelink object
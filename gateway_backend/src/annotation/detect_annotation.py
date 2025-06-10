import re
from typing import List, Dict, Any
from ..objects.text_object import AnnotationLink, BoundingBox

class AnnotationDetector:
    """
    detects annotation references and their corresponding definitions and returns
    a list of structured AnnotationLink objects.
    """
    def __init__(self):
        self.ref_pattern = re.compile(r'(\[\d+\]|\(\d+\)|\b\d+\b)')  # for reference
        self.def_pattern = re.compile(r'^\s*(\d+)\.\s+')  # for definition

    def detect(self, processed_data: Dict[str, Any]) -> List[AnnotationLink]:
        all_references = []
        all_definitions = {} # Maps a key (e.g., '1') to its full definition text
        
        for page_content in processed_data.get("pages", []):
            page_num = page_content.get("page_num")
            if page_num is None:
                continue # skip if a page has no number

            page_height = page_content.get("dimensions", [0, 800])[1]
            footnote_threshold = page_height * 0.8  # Heuristic for text at the bottom

            for block in page_content.get("blocks", []):
                text = block.get('text', '')
                bbox = block.get('bbox', [])

                # detecting definition pattern out of whole txt
                def_match = self.def_pattern.match(text)
                # currently assuming annotations sit at the bottom of pages
                if def_match and bbox and bbox[1] > footnote_threshold:
                    key = def_match.group(1)
                    definition_text = self.def_pattern.sub('', text).strip()
                    if key not in all_definitions:
                        all_definitions[key] = definition_text
                
                # going through text blocks to detect reference pattern
                for ref_match in self.ref_pattern.finditer(text):
                    ref_text_with_brackets = ref_match.group(0)
                    ref_key = re.sub(r'[\(\)\[\]]', '', ref_text_with_brackets)
                    
                    # may need to be refined for better accuracy
                    all_references.append({
                        'key': ref_key,
                        'page': page_num,
                        'bbox': bbox 
                    })

        # create actual AnnotationLink instances
        final_links: List[AnnotationLink] = []
        for ref in all_references:
            key = ref['key']
            if key in all_definitions and ref.get('bbox'): # Ensure bbox exists
                link = AnnotationLink(
                    page_num=ref['page'],
                    reference_bbox=BoundingBox(
                        x0=ref['bbox'][0], 
                        y0=ref['bbox'][1], 
                        x1=ref['bbox'][2], 
                        y1=ref['bbox'][3]
                    ),
                    target_text=all_definitions[key]
                )
                final_links.append(link)
        
        return final_links

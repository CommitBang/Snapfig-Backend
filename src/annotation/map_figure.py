import re
from typing import List, Dict, Any, Optional
from ..objects.text_object import FigureLink, BoundingBox

class FigureMapper:
    """
    finds references to figures/tables, links them to the actual images,
    returns a list of structured FigureLink objects.
    f
    """
    def __init__(self):
        self.ref_pattern = re.compile(
            r'(?:see|in|as shown in)\s+(Figure|Fig|Table|Chart)\.?\s+(\d+(?:\.\d+)?)', re.IGNORECASE
        )
        self.caption_pattern = re.compile(
            r'^(Figure|Fig|Table|Chart)\.?\s+(\d+(?:\.\d+)?[:\.\s])', re.IGNORECASE
        )

    def _find_closest_image_to_caption(self, caption_bbox: List[float], image_blocks: List[Dict], page_height: float) -> Optional[Dict]:
        closest_image = None
        min_dist = float('inf')

        for image in image_blocks:
            img_bbox = image['bbox']
            is_above = img_bbox[3] < caption_bbox[1]
            vertical_dist = caption_bbox[1] - img_bbox[3]
            horizontal_overlap = max(0, min(img_bbox[2], caption_bbox[2]) - max(img_bbox[0], caption_bbox[0]))
            
            # Heuristic: Image should be reasonably close above the caption and overlap horizontally
            if is_above and horizontal_overlap > 20 and vertical_dist < min_dist and vertical_dist < page_height * 0.2:
                min_dist = vertical_dist
                closest_image = image
        
        return closest_image

    def map_figures(self, processed_data: Dict[str, Any], pdf_filename: str) -> List[FigureLink]:
        all_references = []
        figure_targets = {}  # later will store key to target reference value

        # look through each page to find all possible figure targets
        for page_num_str, content in processed_data.get("pages", {}).items():
            page_num = int(page_num_str)
            page_dims = content.get("dimensions", [0, 800])
            image_blocks_on_page = [b for b in content.get("blocks", []) if b.get('type') == 'image']

            for block in content.get("blocks", []):
                text = block.get('text', '')

                # find all references in the text like "see Figure 1.1"
                for match in self.ref_pattern.finditer(text):
                    key = f"{match.group(1).capitalize()} {match.group(2)}"
                    all_references.append({
                        "key": key,
                        "page": page_num,
                        "bbox": block.get('bbox')
                    })
                
                # find all captions and link them to their image to create targets
                caption_match = self.caption_pattern.match(text)
                if caption_match:
                    key = f"{caption_match.group(1).capitalize()} {caption_match.group(2).strip(':. ')}"
                    if key not in figure_targets: # Only process each caption once
                        linked_image = self._find_closest_image_to_caption(block.get('bbox'), image_blocks_on_page, page_dims[1])
                        if linked_image and linked_image.get("xref"):
                            figure_targets[key] = {"xref": linked_image.get("xref")}

        final_links = []  # list of FigureLink objecst
        for ref in all_references:
            key = ref['key']
            if key in figure_targets:
                target_xref = figure_targets[key]['xref']
                link = FigureLink(
                    page_num=ref['page'],
                    reference_bbox=BoundingBox(
                        x0=ref['bbox'][0], 
                        y0=ref['bbox'][1], 
                        x1=ref['bbox'][2], 
                        y1=ref['bbox'][3]
                    ),
                    target_xref=target_xref,
                    pdf_filename=pdf_filename
                )
                final_links.append(link)
                
        return final_links
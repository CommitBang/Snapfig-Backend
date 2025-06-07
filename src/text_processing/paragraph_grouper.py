from typing import List, Dict, Any

class ParagraphGrouper:
    def _in_same_paragraph(self, prev_line_bbox: List[float], current_line_bbox: List[float]) -> bool:
        px0, py0, px1, py1 = prev_line_bbox
        cx0, cy0, cx1, cy1 = current_line_bbox
        
        # two heuristics used, one vertical distance and the other horizontal line-up
        # hueristic1 : vertically close enough?
        vertical_gap = cy0 - py1
        line_height = py1 - py0
        
        # A standard line break should have a gap less than the height of the line itself.
        if vertical_gap < 0 or vertical_gap > (line_height * 0.8):  # might have to modify this accordingly 
            return False

        # heuristic2 : horizontally on the same line?
        horizontal_diff = abs(cx0 - px0)
        if horizontal_diff > 30:  # modify this according to result
            return False

        return True

    def _combine_bboxes(self, bbox1: List[float], bbox2: List[float]) -> List[float]:
        x0 = min(bbox1[0], bbox2[0])
        y0 = min(bbox1[1], bbox2[1])
        x1 = max(bbox1[2], bbox2[2])
        y1 = max(bbox1[3], bbox2[3])
        return [x0, y0, x1, y1]

    # takes in a list of text blocks -> convert it into list of paragraphs. other blocks like image blocks remain unchanged
    def group(self, page_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not page_blocks:
            return []

        # separate text blocks from other types (like images)
        # if not taking account of text blocks in other types, separating and combining of text and those other types has to be done explicitly somewhere else.
        text_lines = [b for b in page_blocks if b.get('type') == 'text']
        other_blocks = [b for b in page_blocks if b.get('type') != 'text']

        if not text_lines:  # no text found
            return other_blocks

        # make sure the blocks are going top to bottom, left to right.
        # this is how human reads
        text_lines.sort(key=lambda b: (b['bbox'][1], b['bbox'][0]))

        grouped_paragraphs = []
        current_paragraph = {
            "type": "text",
            "text": text_lines[0]['text'],
            "bbox": text_lines[0]['bbox']
        }

        for i in range(1, len(text_lines)):
            prev_line = text_lines[i-1]
            current_line = text_lines[i]

            if self._in_same_paragraph(prev_line['bbox'], current_line['bbox']):
                # gathering into one paragraph
                current_paragraph['text'] += " " + current_line['text']
                current_paragraph['bbox'] = self._combine_bboxes(current_paragraph['bbox'], current_line['bbox'])
            else:
                # finalizing the previous paragraph and starting a new one
                grouped_paragraphs.append(current_paragraph)
                current_paragraph = {
                    "type": "text",
                    "text": current_line['text'],
                    "bbox": current_line['bbox']
                }
        # adding the last paragraph explicitly
        grouped_paragraphs.append(current_paragraph)

        return sorted(grouped_paragraphs + other_blocks, key=lambda b: b['bbox'][1])
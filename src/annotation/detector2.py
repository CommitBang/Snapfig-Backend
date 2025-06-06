import json
import re
import os

def find_and_match_figures(json_path):
    """
    JSON 파일의 'paragraphs' 필드에서 'Figure X.xx' 또는 'Fig. X.xx' 패턴을 검색하고
    X.xx 넘버와 매칭하여 페이지 정보를 포함하여 저장합니다.

    Args:
        json_path (str): JSON 파일 경로.

    Returns:
        dict: 매칭된 'Figure X.xx' 또는 'Fig. X.xx'와 X.xx 넘버 및 페이지 정보의 딕셔너리.
    """
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        figure_matches = {}

        # 각 페이지의 'paragraphs' 필드에서 텍스트 추출
        for page in data:
            page_number = page.get("page", None)
            paragraphs = page.get("paragraphs", [])
            for text in paragraphs:
                # 정규식으로 'Figure X.xx' 또는 'Fig. X.xx' 패턴 검색
                match = re.search(r'(Figure|Fig)\.?\s(\d+\.\d+)', text)
                if match:
                    figure_type = match.group(1)  # 'Figure' 또는 'Fig'
                    figure_number = match.group(2)  # 'X.xx'
                    figure_matches[f"{figure_type} {figure_number}"] = {
                        "number": figure_number,
                        "page": page_number
                    }
        
        return figure_matches
    except Exception as e:
        print(f"JSON 파일 처리 중 오류 발생: {e}")
        return {}

import json
import re

def find_and_match_figures(json_path):
    """
    JSON 파일의 'rec_texts' 필드에서 'Figure X.xx' 또는 'Fig. X.xx' 패턴을 검색하고
    X.xx 넘버와 매칭하여 저장합니다.
    
    Args:
        json_path (str): JSON 파일 경로.
    
    Returns:
        dict: 매칭된 'Figure X.xx' 또는 'Fig. X.xx'와 X.xx 넘버의 딕셔너리.
    """
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        rec_texts = data.get('overall_ocr_res', {}).get('rec_texts', [])
        figure_matches = {}

        # 정규식으로 'Figure X.xx' 또는 'Fig. X.xx' 패턴 검색
        for text in rec_texts:
            match = re.search(r'(Figure|Fig)\.?\s(\d+\.\d+)', text)
            if match:
                figure_type = match.group(1)  # 'Figure' 또는 'Fig'
                figure_number = match.group(2)  # 'X.xx'
                figure_matches[f"{figure_type} {figure_number}"] = figure_number
        
        return figure_matches
    except Exception as e:
        print(f"JSON 파일 처리 중 오류 발생: {e}")
        return {}

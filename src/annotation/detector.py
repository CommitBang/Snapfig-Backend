import json
import re
import os

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

def extract_figure_title_blocks(json_path):
    """
    JSON 파일에서 parsing_res_list 내 block_label이 'figure_title'인 블록들을 추출합니다.

    Args:
        json_path (str): JSON 파일 경로.

    Returns:
        list: 'figure_title' 블록들의 리스트.
    """
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        parsing_res_list = data.get('parsing_res_list', [])
        
        figure_title_blocks = [
            block for block in parsing_res_list if block.get("block_label") == "figure_title"
        ]
        
        return figure_title_blocks
    except Exception as e:
        print(f"Figure Title Blocks 추출 중 오류 발생: {e}")
        return []

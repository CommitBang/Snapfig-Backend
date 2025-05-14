import os
from typing import List, Dict, Any
import json
import time

def ensure_upload_folder(app) -> None:
    """
    업로드 폴더가 존재하는지 확인하고 없으면 생성합니다.
    """
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def cleanup_old_files(folder: str, max_age: int = 3600) -> None:
    """
    지정된 시간보다 오래된 파일들을 정리합니다.
    
    Args:
        folder: 정리할 폴더 경로
        max_age: 파일의 최대 보관 시간(초), 기본값 1시간
    """
    current_time = time.time()
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            if current_time - os.path.getmtime(filepath) > max_age:
                os.remove(filepath)

def save_processing_result(result: Dict[str, Any], output_path: str) -> None:
    """
    처리 결과를 JSON 파일로 저장합니다.
    
    Args:
        result: 저장할 처리 결과 딕셔너리
        output_path: 저장할 파일 경로
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2) 
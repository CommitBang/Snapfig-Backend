import requests
from flask import current_app
import os
from typing import List, Dict, Any
import json
import time
import fitz

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


def summarize_text_via_service(text: str):
    service_url = f"{current_app.config['OCR_SERVICE_URL']}/summarize_text"
    try:
        response = requests.post(service_url, json={'text': text}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        return {"error": "Failed to connect to summarization service", "details": str(e)}
    
def summarize_figure_via_service(pdf_filename: str, xref: int):
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_filename)
    if not os.path.exists(filepath):
        return {"error": "Original PDF file not found on server."}

    # extract the image bytes from the PDF using PyMuPDF and the xref
    try:
        doc = fitz.open(filepath)
        img_data = doc.extract_image(xref)
        image_bytes = img_data["image"]
        doc.close()
    except Exception as e:
        return {"error": "Failed to extract image from PDF.", "details": str(e)}

    service_url = f"{current_app.config.get('OCR_SERVICE_URL')}/summarize_figure"
    if not service_url:
        return {"error": "AI Service URL is not configured."}

    # The ocr_server expects multipart/form-data with an 'image' file part.
    # We don't have OCR text to send from here, so we send an empty list.
    files_to_forward = {'image': ('figure.png', image_bytes, 'image/png')}
    form_data = {'ocr_texts': json.dumps([])}

    try:
        response = requests.post(service_url, files=files_to_forward, data=form_data, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Could not connect to figure summarization service: {e}")
        return {"error": "The summarization service is currently unavailable.", "details": str(e)}

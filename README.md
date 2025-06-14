# Snapfig Backend

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.0+-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-APACH-yellow.svg)](LICENSE)

## 📖 프로젝트 소개

SnapFig는 PDF 문서 내 다양한 요소(그림, 표, 수식 등)를 자동으로 감지하고, 참조 구문(Fig. 1 등)과 실제 시각적 객체를 연결해주는 AI 기반 문서 분석 시스템입니다.
OCR 기반 텍스트 추출, PDF 문서 구조 자동 분석, 주석–Figure 매핑 & 팝업 기능을 제공하여
사용자는 복잡한 학술 PDF 문서에서도 "Fig. 2"와 같은 텍스트를 클릭하거나 검색하여 사용자가 중요한 내용과 그림을 빠르게 찾아보고 관리할 수 있게 합니다.

이러한 기능은 문서 구조 감지 + 자동 매핑 + 시각적 요소와의 연결까지 통합적으로 제공하는 점에서 큰 차별점을 가집니다.

---

## 목차

- [주요 기능](#-주요-기능)
- [프로젝트 구조](#-프로젝트-구조)
- [사용 방법](#-사용-방법)
- [빠른 시작](#-빠른-시작)
- [라이센스](#-라이센스)

## 🚀 주요 기능

### 텍스트 전처리 및 문단 정리

- **PDF 문서에서 텍스트 추출 및 정규화**
- **문단 구조 분석 및 재구성**
- **특수 문자 및 포맷 처리**
- **주석 탐지 및 Figure 매핑**

### 문서 내 주석 자동 탐지
- **Figure 참조와 실제 이미지 매핑**
- **상호 참조 분석**
---
## 📁 프로젝트 구조
```
📦Backend
 ┣ 📂config
 ┃ ┗ 📜default.py
 ┣ 📂src
 ┃ ┣ 📂annotation                  # 주석 처리 모듈
 ┃ ┃ ┣ 📜detect_annotation.py      # 주석 탐지
 ┃ ┃ ┣ 📜map_figure.py             # Figure 매핑
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📂api                         # API 통합 모듈
 ┃ ┃ ┣ 📜routes.py                 # API 라우트
 ┃ ┃ ┗ 📜utils.py                  # 유틸리티 함수
 ┃ ┣ 📂objects                     # 객체화 모듈
 ┃ ┃ ┗ 📜text_object.py            # 텍스트 객체화
 ┃ ┣ 📂services                    # OCR 처리 서비스
 ┃ ┃ ┗ 📜ocr_service.py
 ┃ ┣ 📂text_processing             # 텍스트 처리 모듈
 ┃ ┃ ┣ 📜paragraph_grouper.py      # 문단 분석
 ┃ ┃ ┣ 📜preprocessor.py           # 텍스트 전처리
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┗ 📜main.py                     # 서버 실행
 ┣ 📜.gitignore
 ┣ 📜README.md
 ┗ 📜requirements.txt              #의존성 정의
```
---
## 🎯사용 방법
1. 저장소 클론
```
git clone [repository-url]
cd Backend
```
2. 가상환경 생성 및 활성화
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```
3. 의존성 설치
```
pip install -r requirements.txt
```
- 핵심 의존성
```
PyPDF2==3.0.1            # PDF 파일에서 텍스트, 메타데이터 추출 및 페이지 분할 등을 위한 라이브러리
pdf2image==1.16.3        # PDF 페이지를 이미지로 변환 (OCR 전처리를 위해 사용)
pytesseract==0.3.10      # Tesseract OCR 엔진의 Python 바인딩 (이미지에서 텍스트 추출)
numpy==1.24.4            # 수치 계산, 배열 연산 등 전반적인 데이터 처리용 필수 라이브러리
spacy==3.6.0             # 고성능 자연어 처리(NLP)를 위한 라이브러리 (문장 구조 분석, 개체명 인식 등)
nltk==3.8.1              # 전통적인 텍스트 분석을 위한 NLP 툴킷 (토큰화, 형태소 분석 등)
scikit-learn==1.3.0      # 머신러닝 모델 구축 및 벡터화, 분류, 클러스터링 등 다양한 알고리즘 제공

flask==2.3.3             # Python 기반의 경량 웹 프레임워크 (RESTful API 서버 구축에 사용)
python-dotenv==1.0.0     # 환경변수(.env 파일) 로드용 라이브러리 (설정값 외부화)

pytest==7.4.0            # Python 테스트 프레임워크 (단위 테스트 자동화 및 테스트 스크립트 작성)
black==23.7.0            # 코드 포매터 (PEP8 스타일에 맞게 자동 정렬)
isort==5.12.0            # import 구문 자동 정렬 도구
flake8==6.1.0            # 코드 스타일 검사 도구 (문법 오류, 스타일 위반 탐지)

```
4. 추가 필요 사항

- Tesseract OCR 엔진 설치 필요
- SpaCy 언어 모델 다운로드:
 ```
 python -m spacy download ko_core_news_lg
 ```
---
## 빠른 시작
1. 서버 실행
```
python -m src.main
```

2. API 사용
#### Upload and Process pdf
```
curl -X POST \
  http://localhost:5000/api/v1/process \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```
- Python 예제
```
import requests

# Upload PDF for analysis
url = "http://localhost:5000/api/v1/process"
with open("your_document.pdf", "rb") as file:
    files = {"file": file}
    response = requests.post(url, files=files)

result = response.json()

# Access OCR and annotation results
paragraphs = result.get("paragraph_data", {})
interactive_elements = result.get("interactive_elements", [])

print(f"Total Pages: {len(paragraphs.get('pages', []))}")
print(f"Detected Interactive Elements: {len(interactive_elements)}")
```

#### Text Summarization
- Python 예제
```
url = "http://localhost:5000/api/v1/summarize/figure"
data = {"pdf_filename": "your_document.pdf", "xref": 17}
response = requests.post(url, json=data)
print(response.json())
```
#### Figure Summarization
- Python 예제
```
url = "http://localhost:5000/api/v1/summarize/figure"
data = {"pdf_filename": "your_document.pdf", "xref": 17}
response = requests.post(url, json=data)
print(response.json())
```
---

## 📚 API Documentation
### 📄 Endpoints
- **POST /api/v1/process** : PDF 문서를 업로드하여 분석
- **POST /api/v1/summarize/text** : 텍스트 요약
- **POST /api/v1/summarize/figure** : PDF 내 특정 그림 요소 요약

- Response Codes:

  200: 성공

  400: 잘못된 형식 또는 누락

  500: 실패 또는 내부 오류

---
## 📄 라이센스
This project is licensed under the APACH License - see the [LICENSE](License) file for details.

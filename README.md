# Advanced PDF Viewer and Analyzer

고급 PDF 문서 분석 및 처리 시스템으로, 텍스트 전처리와 주석 탐지 기능을 제공합니다.

## 주요 기능

1. **텍스트 전처리 및 문단 정리**
   - PDF 문서에서 텍스트 추출 및 정규화
   - 문단 구조 분석 및 재구성
   - 특수 문자 및 포맷 처리

2. **주석 탐지 및 Figure 매핑**
   - 문서 내 주석 자동 탐지
   - Figure 참조와 실제 이미지 매핑
   - 상호 참조 분석

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd advanced-pdf-viewer
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 추가 필요 사항
- Tesseract OCR 엔진 설치 필요
- SpaCy 언어 모델 다운로드:
  ```bash
  python -m spacy download ko_core_news_lg
  ```

## 사용 방법

1. 서버 실행
```bash
python src/main.py
```

2. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 프로젝트 구조

```
advanced-pdf-viewer/
├── src/
│   ├── text_processing/     # 텍스트 처리 모듈
│   │   ├── preprocessor.py  # 텍스트 전처리
│   │   └── paragraph.py     # 문단 분석
│   ├── annotation/         # 주석 처리 모듈
│   │   ├── detector.py     # 주석 탐지
│   │   └── mapper.py       # Figure 매핑
│   └── api/               # API 통합 모듈
│       ├── routes.py      # API 라우트
│       └── utils.py       # 유틸리티 함수
├── tests/                 # 테스트 코드
├── docs/                 # 문서화
├── config/              # 설정 파일
└── requirements.txt    # 의존성 정의
```

## 개발 가이드라인

- Black을 사용한 코드 포맷팅
- Flake8을 통한 코드 검사
- 테스트 주도 개발(TDD) 권장
- Git 커밋 메시지 컨벤션 준수

## 라이선스

MIT License

## 기여 방법

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 
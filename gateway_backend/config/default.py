import os

# Application settings
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Processing settings
TESSERACT_CMD = os.getenv('TESSERACT_CMD', 'tesseract')
SPACY_MODEL = 'ko_core_news_lg'

# API settings
API_VERSION = 'v1'
API_TITLE = 'Advanced PDF Viewer API'
API_PREFIX = f'/api/{API_VERSION}'

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'app.log' 

# must validate this to correctly route to ocr service(currently set to local desktop not lab server)
OCR_SERVICE_URL = "http://localhost:5001/ocr"
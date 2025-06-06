# api/routes.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename 
import os

from services.ocr_service import OCRService
from text_processing.preprocessor import TextPreprocessor
from annotation.detect_annotation import AnnotationDetector
from annotation.map_figure import FigureMapper
from .utils import summarize_text_via_service
from .utils import summarize_figure_via_service

api = Blueprint('api', __name__)

@api.route('/process', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            ocr_service = OCRService()
            text_processor = TextPreprocessor()
            annotation_detector = AnnotationDetector()
            figure_mapper = FigureMapper()

            raw_ocr_json = ocr_service.process_pdf(filepath)  # raw json
            processed_data = text_processor.preprocess(raw_ocr_json)  # dictionary
            
            detected_annotations = annotation_detector.detect(processed_data)
            figure_mappings = figure_mapper.map_figures(processed_data, filepath)

            return jsonify({
                "annotations": detected_annotations,
                "figures": figure_mappings
            }), 200

        except Exception as e:
            current_app.logger.error(f"An error occurred during PDF processing: {e}", exc_info=True)
            return jsonify({'error': 'Failed to process PDF.', 'details': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@api.route('/summarize/text', methods=['POST'])
def summarize_text_route():
    request_data = request.get_json()
    if not request_data or 'text' not in request_data:
        return jsonify({'error': 'Request body must be JSON and contain a "text" field.'}), 400
    
    text_to_summarize = request_data['text']
    summary_result = summarize_text_via_service(text_to_summarize)

    if 'error' in summary_result:
        return jsonify(summary_result), 503  # 503 Service Unavailable

    return jsonify(summary_result), 200

@api.route('/summarize/figure', methods=['POST'])
def summarize_figure_route():
    request_data = request.get_json()
    if not request_data:
        return jsonify({'error': 'Request body must be JSON.'}), 400
    
    pdf_filename = request_data.get('pdf_filename')
    xref = request_data.get('xref')

    if not pdf_filename or not xref:
        return jsonify({'error': 'Request body must contain "pdf_filename" and "xref".'}), 400

    summary_result = summarize_figure_via_service(pdf_filename, int(xref))

    if 'error' in summary_result:  # return a server error if the process failed
        return jsonify(summary_result), 500

    return jsonify(summary_result), 200
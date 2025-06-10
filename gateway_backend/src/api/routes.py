# api/routes.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename 
import os

from ..services.ocr_service import OCRService
from ..text_processing.preprocessor import TextPreprocessor
from ..text_processing.paragraph_grouper import ParagraphGrouper
from ..annotation.detect_annotation import AnnotationDetector
from ..annotation.map_figure import FigureMapper
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
    
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file format'}), 400
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        ocr_service = OCRService()
        raw_ocr_json = ocr_service.process_pdf(filepath)
        
        # group the paragraph with ocr'd result first. the result is too granular
        grouper = ParagraphGrouper()
        for page_data in raw_ocr_json.get("pages", []):
            page_data["blocks"] = grouper.group(page_data.get("blocks", []))
        
        # raw json format turned into paragraph-wise list.
        paragraph_data = raw_ocr_json

        annotation_detector = AnnotationDetector()
        figure_mapper = FigureMapper()
        
        detected_annotations = annotation_detector.detect(paragraph_data)
        figure_mappings = figure_mapper.map_figures(paragraph_data, filename)

        interactive_elements = detected_annotations + figure_mappings
        # convert the list of objects to a list of dictionaries for JSON
        json_payload = [element.to_dict() for element in interactive_elements]

        # return both the interactive elements and the full paragraph data.
        return jsonify({
            "interactive_elements": json_payload,
            "paragraph_data": paragraph_data 
        }), 200

    except Exception as e:
        current_app.logger.error(f"An error occurred during PDF processing: {e}", exc_info=True)
        return jsonify({'error': 'Failed to process PDF.', 'details': str(e)}), 500

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
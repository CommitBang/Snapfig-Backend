from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import requests

from text_processing import TextPreprocessor, ParagraphSummarizer
from annotation import AnnotationDetector, FigureMapper

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
        
        # Process the PDF
        text_processor = TextPreprocessor()
        paragraph_summarizer = ParagraphSummarizer()
        
        # Text processing
        extracted_data : dict = text_processor.extract_json_via_ocr_server(filepath)
        processed_data = text_processor.preprocess(extracted_data)  # gather text from json, return figures and annotations
        #paragraphs =
        #annotations =
        #figures = 

        summarized_paragraphs = paragraph_summarizer.analyze(processed_data)
        
        # Annotation processing
        annotation_detector = AnnotationDetector()  # assumed to be aggregated in text processing
        figure_mapper = FigureMapper()
        
        annotations = annotation_detector.detect(processed_data)
        figure_mappings = figure_mapper.map_figures(annotations, filepath)
        
        return jsonify({
            'paragraphs': paragraphs,
            'annotations': annotations,
            'figure_mappings': figure_mappings
        }), 200
    
    return jsonify({'error': 'Invalid file format'}), 400 
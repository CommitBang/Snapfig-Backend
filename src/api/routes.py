from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from text_processing import TextPreprocessor, ParagraphAnalyzer
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
        paragraph_analyzer = ParagraphAnalyzer()
        
        # Text processing
        extracted_text = text_processor.extract_text(filepath)
        processed_text = text_processor.preprocess(extracted_text)
        paragraphs = paragraph_analyzer.analyze(processed_text)
        
        # Annotation processing
        annotation_detector = AnnotationDetector()
        figure_mapper = FigureMapper()
        
        annotations = annotation_detector.detect(processed_text)
        figure_mappings = figure_mapper.map_figures(annotations, filepath)
        
        return jsonify({
            'paragraphs': paragraphs,
            'annotations': annotations,
            'figure_mappings': figure_mappings
        }), 200
    
    return jsonify({'error': 'Invalid file format'}), 400 
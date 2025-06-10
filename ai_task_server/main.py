from flask import Flask, request, jsonify
from PIL import Image
import os
import json
from pdf_processor import PDFProcessor
from figure_summarizer import FigureSummarizer
from text_summarizer import TextSummarizer 

app = Flask(__name__)

# ai services loaded here
PDF_PROCESSOR_INSTANCE = PDFProcessor()
SUMMARIZER_INSTANCE = FigureSummarizer()
TEXT_SUMMARIZER_INSTANCE = TextSummarizer() 


@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    pdf_file = request.files['file']
    if not pdf_file or pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    try:
        pdf_bytes = pdf_file.read()
        structured_json = PDF_PROCESSOR_INSTANCE.process(pdf_bytes)
        return jsonify(structured_json), 200
    except Exception as e:
        app.logger.error(f"OCR process failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to process PDF", "details": str(e)}), 500


@app.route('/summarize_figure', methods=['POST'])
def summarize_figure_endpoint():
    if 'image' not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400
    image_file = request.files['image']
    ocr_texts_str = request.form.get('ocr_texts', '[]')
    try:
        ocr_texts = json.loads(ocr_texts_str)
        if not isinstance(ocr_texts, list):
            raise ValueError("ocr_texts must be a list.")
        image = Image.open(image_file.stream)
        summary = SUMMARIZER_INSTANCE.summarize(image=image, ocr_texts=ocr_texts)
        if summary.startswith("Error:"):
            return jsonify({"error": "Figure summarization failed", "details": summary}), 500
        return jsonify({"summary": summary}), 200
    except Exception as e:
        app.logger.error(f"Summarization endpoint failed: {e}", exc_info=True)
        return jsonify({"error": "Figure summarization failed", "details": str(e)}), 500

@app.route('/summarize_text', methods=['POST'])
def summarize_text_endpoint():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    
    text_to_summarize = data['text']
    try:
        summaries = TEXT_SUMMARIZER_INSTANCE.summarize(text_to_summarize)
        return jsonify({"summaries": summaries}), 200
    except Exception as e:
        app.logger.error(f"Text summarization failed: {e}", exc_info=True)
        return jsonify({"error": "Text summarization failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
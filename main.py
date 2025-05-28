# main.py
from flask import Flask, request, jsonify
from ocr_pdf import extract_text_from_pdf
from figure_summarizer import summarize_figure_with_ocr, load_model_and_processor as load_summarizer_model # Renamed for clarity
import json # For parsing ocr_texts
import os
import tempfile # For handling uploaded image files

app = Flask(__name__)

# Configuration for uploaded files
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files['file']
    if not pdf_file or pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        pdf_bytes = pdf_file.read()
        pages = extract_text_from_pdf(pdf_bytes) # from ocr_pdf.py
        return jsonify({"pages": pages}), 200
    except Exception as e:
        app.logger.error(f"OCR failed: {e}")
        return jsonify({"error": "OCR failed", "details": str(e)}), 500

@app.route('/summarize_figure', methods=['POST'])
def summarize_figure_endpoint():
    if 'image' not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    image_file = request.files['image']
    if not image_file or image_file.filename == '':
        return jsonify({"error": "No selected image file"}), 400

    ocr_texts_str = request.form.get('ocr_texts', '[]') # Default to empty JSON list string
    ocr_texts = []
    try:
        ocr_texts = json.loads(ocr_texts_str)
        if not isinstance(ocr_texts, list):
            return jsonify({"error": "ocr_texts should be a JSON list of strings"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format for ocr_texts"}), 400

    # Save the uploaded image to a temporary file
    # as summarize_figure_with_ocr currently expects a file path
    filename = image_file.filename
    temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        image_file.save(temp_image_path)
        
        # Call the summarization function from figure_summarizer.py
        summary = summarize_figure_with_ocr(image_path=temp_image_path, ocr_texts=ocr_texts)
        
        if summary.startswith("Error:"):
             return jsonify({"error": "Figure summarization failed", "details": summary}), 500
        
        return jsonify({"summary": summary}), 200

    except Exception as e:
        app.logger.error(f"Figure summarization endpoint failed: {e}")
        return jsonify({"error": "Figure summarization failed", "details": str(e)}), 500
    finally:
        # Clean up the temporary image file
        if os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
            except Exception as e_remove:
                app.logger.error(f"Error removing temporary file {temp_image_path}: {e_remove}")


if __name__ == '__main__':
    print("Loading OCR engine (PaddleOCR)...")
    print("Loading Figure Summarization engine (Florence-2)...")
    load_summarizer_model() # from figure_summarizer.py
    
    app.run(host='0.0.0.0', port=5001)

    
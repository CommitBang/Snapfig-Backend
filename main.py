# main.py
from flask import Flask, request, jsonify
from ocr_engine import extract_text_from_pdf

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files['file']
    try:
        pages = extract_text_from_pdf(pdf_file.read())
        return jsonify({"pages": pages}), 200
    except Exception as e:
        return jsonify({"error": "OCR failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

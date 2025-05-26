# test_client.py
import requests

pdf_path = r"C:\Users\USER\general\3-1 SE\26 Exception Handling.pdf" 

ocr_url = "http://localhost:5001/ocr"  
with open(pdf_path, "rb") as f:
    response = requests.post(ocr_url, files={"file": f})

if response.status_code == 200:
    data = response.json()
    for i, page_text in enumerate(data["pages"], start=1):
        print(f"\n--- Page {i} ---")
        print(page_text)
else:
    print(f"❌ OCR failed: {response.status_code}")
    print(response.text)

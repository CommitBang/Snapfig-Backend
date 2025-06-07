# figure_summarizer.py
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from typing import List, Optional

class FigureSummarizer:
    def __init__(self):
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model_and_processor()

    def _load_model_and_processor(self):
        if self.model is not None:
            return

        model_id = "nlpconnect/vit-gpt2-image-captioning"
        
        self.model = VisionEncoderDecoderModel.from_pretrained(model_id).to(self.device)
        self.processor = ViTImageProcessor.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
    def summarize(self, image: Image.Image, ocr_texts: Optional[List[str]] = None) -> str:
        if not self.model or not self.processor or not self.tokenizer:
            return "Error: Summarizer model not loaded."

        try:
            image_rgb = image.convert("RGB")
            
            # process the image
            pixel_values = self.processor(images=[image_rgb], return_tensors="pt").pixel_values.to(self.device)
            
            # generate the caption IDs
            generated_ids = self.model.generate(pixel_values, max_new_tokens=50) # Keep captions concise
            
            # decode the IDs to get the text
            generated_text = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

            return generated_text.strip()

        except Exception as e:
            return f"Error during model inference: {str(e)}"
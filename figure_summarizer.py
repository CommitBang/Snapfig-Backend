# figure_summarizer.py
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import torch
from typing import List, Optional
import os

class FigureSummarizer:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model_and_processor()

    def _load_model_and_processor(self):
        if self.processor is not None and self.model is not None:
            return

        model_id = "microsoft/Florence-2-base"
        gpu_profile = os.environ.get("GPU_PROFILE", "4060").upper()

        load_kwargs = {"trust_remote_code": True}
        if self.device == "cuda":
            if gpu_profile == "3090":
                load_kwargs["torch_dtype"] = torch.float16
            else: # Default for 4060 (3090 for lab) or other
                load_kwargs["load_in_8bit"] = True
            load_kwargs["device_map"] = "auto"
        else:
            load_kwargs["device_map"] = self.device

        self.model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

    def summarize(self, image: Image.Image, ocr_texts: Optional[List[str]] = None) -> str:
        if not self.model or not self.processor:
            return "Error: Summarizer model not loaded."

        try:
            image_rgb = image.convert("RGB")
           
            prompt = "<MORE_DETAILED_CAPTION>"
            
            if ocr_texts:
                # can consider handling bit of text here
                pass

            inputs = self.processor(text=prompt, images=image_rgb, return_tensors="pt").to(self.device)

            generated_ids = self.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=512,
                num_beams=3
            )
            summary_list = self.processor.batch_decode(generated_ids, skip_special_tokens=False)
            parsed_caption = self.processor.post_process_generation(summary_list[0], task=prompt, image_size=image.size)
            final_caption = parsed_caption.get(prompt, "Could not generate caption.")

            return final_caption

        except Exception as e:
            print(f"ERROR in FigureSummarizer.summarize: {e}")
            return f"Error during model inference: {str(e)}"
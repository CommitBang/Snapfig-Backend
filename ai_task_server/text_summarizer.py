from typing import List
from transformers import pipeline

class TextSummarizer:
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        # currently explicitly assigned to CPU to not interfere with GPU memory for vision models.
        # maybe quantization or enough vram enables gpu
        self.summarizer = pipeline("summarization", model=model_name, device=-1)  # -1 here indicates it is set to cpu

    def _split_into_paragraphs(self, text: str) -> List[str]:
        return [p.strip() for p in text.split('\n') if len(p.strip()) > 20]

    def summarize(self, text_to_summarize: str) -> List[dict]:
        paragraphs = self._split_into_paragraphs(text_to_summarize)
        summaries = []
        for para in paragraphs:
            try:
                # returning a list of dicts is more structured and consistent.
                summary_text = self.summarizer(
                    para,
                    max_length=100,
                    min_length=20,
                    do_sample=False
                )[0]['summary_text']
                summaries.append({"original": para, "summary": summary_text})
            except Exception as e:
                print(f"Could not summarize paragraph: {e}")
                summaries.append({"original": para, "summary": "Summarization failed."})
        return summaries
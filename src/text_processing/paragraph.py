# paragraph.py
from typing import List
from transformers import pipeline

class ParagraphSummarizer:
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.summarizer = pipeline("summarization", model=model_name)

    def split_into_paragraphs(self, text: str) -> List[str]:  # assumed to take the entire script on the page
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]  # split assuming paragraphs will be divided by /n/n 
        return paragraphs

    def summarize_paragraphs(self, paragraphs: List[str]) -> List[str]:
        summaries = []
        for para in paragraphs:
            try:
                summary = self.summarizer(  # calls summarization model
                    para,
                    max_length=80,   # output up to 80 tokens
                    min_length=20,   # output at least 20 tokens
                    do_sample=False  # deterministic output(no random output)
                )[0]['summary_text']
            except Exception:  # too long or model failure
                summary = para[:80] + "..."  
            summaries.append(summary)
        return summaries

    def summarize_text(self, text: str) -> List[str]:
        paragraphs = self.split_into_paragraphs(text)
        return self.summarize_paragraphs(paragraphs)

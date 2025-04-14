"""
Utilități pentru sumarizarea textului în aplicația de analiză a topicurilor
"""
from transformers import pipeline
import torch

# Verifică dacă MPS (GPU-ul Apple) este disponibil și setează dispozitivul în consecință
#device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

model_name = "facebook/bart-large-cnn"
model_revision = "main"

summarizer = pipeline("summarization", model=model_name, revision=model_revision)

def summarize_text(text):
    """
    Sumarizează un text folosind modelul BART
    
    Args:
        text: Textul de sumarizat
        
    Returns:
        Textul sumarizat
    """
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
    return summary[0]['summary_text']

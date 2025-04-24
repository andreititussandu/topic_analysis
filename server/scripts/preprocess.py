"""
Utilități pentru preprocesarea textului în aplicația de analiză a topicurilor
"""
import re
import spacy
import nltk
from nltk.corpus import stopwords

# nltk.download('stopwords') # Descărcă stopwords dacă nu sunt deja instalate

nlp = spacy.load("en_core_web_sm")

# Listă de stopwords suplimentare pentru a îmbunătăți filtrarea
additional_stopwords = [
    "-", "_", "'", "would", "could", "should", "also", "us", "said", "error",
    "please", "ad", "blocker", "site", "always", "however"
]

def preprocess_text(text):
    """
    Preprocesează textul pentru analiza topicurilor
    
    Args:
        text: Textul brut de procesat
        
    Returns:
        Textul procesat, filtrat și lemmatizat
    """
    stop_words = set(stopwords.words('english')).union(set(additional_stopwords)) # Combină stopwords din NLTK cu lista personalizată

    # Elimină caracterele non-alfabetice
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Procesează textul cu spaCy
    doc = nlp(text)

    # Filtrează entitățile numite și etichetele POS nedorite
    filtered_words = []
    for token in doc:
        if token.text.lower() not in stop_words and not token.ent_type_ and token.pos_ in {'NOUN', 'ADJ'}:
            filtered_words.append(token.lemma_)

    return ' '.join(filtered_words)

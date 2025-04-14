"""
Utilități de procesare a textului pentru aplicația de analiză a topicurilor
"""
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_word_frequencies(text):
    """
    Extrage frecvențele cuvintelor pentru norul de cuvinte
    
    Args:
        text: Conținutul textului
        
    Returns:
        Dicționar cu frecvențele cuvintelor
    """
    try:
        words = text.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Include doar cuvintele mai lungi de 3 caractere
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sortează după frecvență și ia primele 100 de cuvinte
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
        return dict(sorted_words)
    except Exception as e:
        logger.error(f"Eroare la extragerea frecvențelor cuvintelor: {str(e)}")
        return {}

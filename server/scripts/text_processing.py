import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_word_frequencies(text):
    try:
        words = text.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
        return dict(sorted_words)
    except Exception as e:
        logger.error(f"Eroare la extragerea frecvențelor cuvintelor: {str(e)}")
        return {}

"""
Text processing utilities for the topic analysis application
"""
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_word_frequencies(text):
    """
    Extract word frequencies for word cloud
    
    Args:
        text: Text content
        
    Returns:
        Dictionary of word frequencies
    """
    try:
        words = text.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only include words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top 100 words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
        return dict(sorted_words)
    except Exception as e:
        logger.error(f"Error extracting word frequencies: {str(e)}")
        return {}

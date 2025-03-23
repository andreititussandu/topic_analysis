"""
Prediction utilities for the topic analysis application
"""
import logging
import uuid
import joblib
import os
from .web_scraper import scrape_text_from_url
from .database import Database
from .text_processing import extract_word_frequencies

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

def predict_topic(url, user_id=None):
    """
    Predict topic for a URL
    
    Args:
        url: URL to predict topic for
        user_id: User ID
        
    Returns:
        Dictionary with prediction results
    """
    if not url:
        return {"error": "No URL provided"}, 400

    # Check cache first
    cached_result = db.check_cache(url)
    if cached_result:
        # Save to history for tracking
        db.save_to_history(url, cached_result.get('text', ''), cached_result.get('prediction', ''), user_id)
        return {
            'predicted_topic': cached_result.get('prediction', ''),
            'word_frequencies': cached_result.get('word_frequencies', {}),
            'from_cache': True
        }, 200

    try:
        text = scrape_text_from_url(url)
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return {"error": f"Failed to scrape {url}: {e}"}, 500

    try:
        with open('./models/model.pkl', 'rb') as model_file:
            model = joblib.load(model_file)
        with open('./models/vectorizer.pkl', 'rb') as vectorizer_file:
            vectorizer = joblib.load(vectorizer_file)

        text_vectorized = vectorizer.transform([text])
        prediction = model.predict(text_vectorized)[0]
        
        # Extract word frequencies for word cloud
        word_frequencies = extract_word_frequencies(text)
        
        # Save to cache
        db.save_to_cache(url, text, prediction, word_frequencies)
        
        # Save to history
        db.save_to_history(url, text, prediction, user_id)

        return {
            'predicted_topic': prediction,
            'word_frequencies': word_frequencies,
            'from_cache': False
        }, 200
    except Exception as e:
        logger.error(f"Error predicting topic: {e}")
        return {"error": f"Error predicting topic: {e}"}, 500

def batch_predict(urls, user_id=None):
    """
    Predict topics for multiple URLs
    
    Args:
        urls: List of URLs to predict topics for
        user_id: User ID
        
    Returns:
        Dictionary with batch prediction results
    """
    if not urls:
        return {"error": "No URLs provided"}, 400
    
    try:
        # Generate a batch ID for grouping
        batch_id = str(uuid.uuid4())
        
        results = []
        for url in urls:
            if not url:
                continue
                
            # Check cache first
            cached_result = db.check_cache(url)
            if cached_result:
                results.append({
                    'url': url,
                    'predicted_topic': cached_result.get('prediction', ''),
                    'from_cache': True
                })
                db.save_to_history(url, cached_result.get('text', ''), cached_result.get('prediction', ''), user_id, batch_id)
                continue
            
            try:
                text = scrape_text_from_url(url)
                
                with open('./models/model.pkl', 'rb') as model_file:
                    model = joblib.load(model_file)
                with open('./models/vectorizer.pkl', 'rb') as vectorizer_file:
                    vectorizer = joblib.load(vectorizer_file)
                
                text_vectorized = vectorizer.transform([text])
                prediction = model.predict(text_vectorized)[0]
                
                # Extract word frequencies
                word_frequencies = extract_word_frequencies(text)
                
                # Save to cache
                db.save_to_cache(url, text, prediction, word_frequencies)
                
                # Save to history
                db.save_to_history(url, text, prediction, user_id, batch_id)
                
                results.append({
                    'url': url,
                    'predicted_topic': prediction,
                    'from_cache': False
                })
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                results.append({
                    'url': url,
                    'error': str(e)
                })
        
        # Group results by topic
        grouped_results = {}
        for result in results:
            if 'error' in result:
                continue
            topic = result['predicted_topic']
            if topic not in grouped_results:
                grouped_results[topic] = []
            grouped_results[topic].append(result['url'])
        
        return {
            'results': results,
            'grouped_results': grouped_results,
            'batch_id': batch_id
        }, 200
        
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        return {"error": f"Error processing batch: {str(e)}"}, 500

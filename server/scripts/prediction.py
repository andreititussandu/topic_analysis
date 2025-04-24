"""
Utilități de predicție pentru aplicația de analiză a topicurilor
"""
import logging
import uuid
import joblib
import os
from .web_scraper import scrape_text_from_url
from .database import Database
from .text_processing import extract_word_frequencies

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inițializare bază de date
db = Database()

def predict_topic(url, user_id=None):
    """
    Prezice topicul pentru un URL
    
    Args:
        url: URL-ul pentru care se face predicția
        user_id: ID-ul utilizatorului
        
    Returns:
        Dicționar cu rezultatele predicției
    """
    if not url:
        return {"error": "Nu a fost furnizat niciun URL"}, 400

    # Verifică mai întâi cache-ul
    cached_result = db.check_cache(url)
    if cached_result:
        # Salvează în istoric pentru urmărire
        db.save_to_history(url, cached_result.get('text', ''), cached_result.get('prediction', ''), user_id)
        return {
            'predicted_topic': cached_result.get('prediction', ''),
            'word_frequencies': cached_result.get('word_frequencies', {}),
            'from_cache': True
        }, 200

    try:
        text = scrape_text_from_url(url)
    except Exception as e:
        logger.error(f"Eșec la extragerea {url}: {e}")
        return {"error": f"Eșec la extragerea {url}: {e}"}, 500

    try:
        with open('./models/model.pkl', 'rb') as model_file:
            model = joblib.load(model_file)
        with open('./models/vectorizer.pkl', 'rb') as vectorizer_file:
            vectorizer = joblib.load(vectorizer_file)

        text_vectorized = vectorizer.transform([text])
        prediction = model.predict(text_vectorized)[0]
        
        # Extrage frecvențele cuvintelor pentru norul de cuvinte
        word_frequencies = extract_word_frequencies(text)
        
        # Salvează în cache
        db.save_to_cache(url, text, prediction, word_frequencies)
        
        # Salvează în istoric
        db.save_to_history(url, text, prediction, user_id)

        return {
            'predicted_topic': prediction,
            'word_frequencies': word_frequencies,
            'from_cache': False
        }, 200
    except Exception as e:
        logger.error(f"Eroare la predicția topicului: {e}")
        return {"error": f"Eroare la predicția topicului: {e}"}, 500

def batch_predict(urls, user_id=None):
    """
    Prezice topicuri pentru multiple URL-uri
    
    Args:
        urls: Lista de URL-uri pentru care se fac predicții
        user_id: ID-ul utilizatorului
        
    Returns:
        Dicționar cu rezultatele predicțiilor în lot
    """
    if not urls:
        return {"error": "Nu au fost furnizate URL-uri"}, 400
    
    try:
        # Generează un ID de lot pentru grupare
        batch_id = str(uuid.uuid4())
        
        results = []
        for url in urls:
            if not url:
                continue
                
            # Verifică mai întâi cache-ul
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
                
                # Extrage frecvențele cuvintelor
                word_frequencies = extract_word_frequencies(text)
                
                # Salvează în cache
                db.save_to_cache(url, text, prediction, word_frequencies)
                
                # Salvează în istoric
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

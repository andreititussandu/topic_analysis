import os
import logging
from .web_scraper import scrape_text_from_url
from .database import Database

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inițializare bază de date
db = Database()

def save_content(url, user_id=None):
    if not url:
        return {"error": "Nu a fost furnizat niciun URL"}, 400
    
    try:
        # Verifică mai întâi dacă există în cache
        cached_result = db.check_cache(url)
        if cached_result and 'text' in cached_result:
            content = cached_result['text']
        else:
            # Dacă nu există în cache, extrage conținutul
            content = scrape_text_from_url(url)
        
        # Creează un nume de fișier bazat pe URL
        filename = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
        if len(filename) > 100:
            filename = filename[:100]
        
        filename = f"{filename}.txt"
        filepath = f"saved_content/{filename}"

        os.makedirs('saved_content', exist_ok=True)
        
        # Salvează conținutul în fișier
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'message': 'Content saved successfully',
            'filename': filename,
            'filepath': filepath
        }, 200
        
    except Exception as e:
        logger.error(f"Error saving content: {str(e)}")
        return {"error": f"Error saving content: {str(e)}"}, 500

def get_file_path(filename):
    try:
        safe_filename = os.path.basename(filename)
        filepath = os.path.join('saved_content', safe_filename)

        if not os.path.exists(filepath):
            return None, "File not found", 404
            
        return filepath, None, 200
    except Exception as e:
        logger.error(f"Error getting file path: {str(e)}")
        return None, f"Error getting file path: {str(e)}", 500

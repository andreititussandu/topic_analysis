"""
Content management utilities for the topic analysis application
"""
import os
import logging
from .web_scraper import scrape_text_from_url
from .database import Database

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

def save_content(url, user_id=None):
    """
    Save content from URL to file
    
    Args:
        url: URL to save content from
        user_id: User ID
        
    Returns:
        Dictionary with save result
    """
    if not url:
        return {"error": "No URL provided"}, 400
    
    try:
        # Check if we have it in cache first
        cached_result = db.check_cache(url)
        if cached_result and 'text' in cached_result:
            content = cached_result['text']
        else:
            # If not in cache, scrape it
            content = scrape_text_from_url(url)
        
        # Create a filename based on the URL
        filename = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
        if len(filename) > 100:
            filename = filename[:100]
        
        filename = f"{filename}.txt"
        filepath = f"saved_content/{filename}"
        
        # Ensure directory exists
        os.makedirs('saved_content', exist_ok=True)
        
        # Save the content to a file
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
    """
    Get safe file path for download
    
    Args:
        filename: Filename to get path for
        
    Returns:
        Tuple of (file_path, error_message, status_code)
    """
    try:
        # Ensure the filename is safe
        safe_filename = os.path.basename(filename)
        filepath = os.path.join('saved_content', safe_filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return None, "File not found", 404
            
        return filepath, None, 200
    except Exception as e:
        logger.error(f"Error getting file path: {str(e)}")
        return None, f"Error getting file path: {str(e)}", 500

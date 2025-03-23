"""
Model training utilities for the topic analysis application
"""
import pandas as pd
import os
import joblib
import shutil
import datetime
import numpy as np
import logging
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.naive_bayes import MultinomialNB
from .web_scraper import scrape_text_from_url
from .database import Database

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

def read_csv(file_path):
    """
    Read CSV file
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Pandas DataFrame or None
    """
    try:
        df = pd.read_csv(file_path)
        logger.info("CSV read successfully")
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return None

def validate_columns(df, required_columns):
    """
    Validate required columns in DataFrame
    
    Args:
        df: Pandas DataFrame
        required_columns: List of required column names
        
    Returns:
        True if all required columns exist, False otherwise
    """
    for column in required_columns:
        if column not in df.columns:
            logger.error(f"Error: Required column '{column}' not found in CSV")
            return False
    return True

def scrape_documents(links):
    """
    Scrape text from URLs
    
    Args:
        links: List of URLs
        
    Returns:
        List of scraped text documents
    """
    documents = []
    for link in links:
        try:
            logger.info(f"Scraping text from URL: {link}")
            text = scrape_text_from_url(link)
            documents.append(text)
        except Exception as e:
            logger.error(f"Failed to scrape {link}: {e}")
            documents.append('')
    return documents

def vectorize_documents(documents):
    """
    Vectorize documents
    
    Args:
        documents: List of text documents
        
    Returns:
        Tuple of (vectorizer, document-term matrix)
    """
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english', ngram_range=(1, 2))
    dtm = vectorizer.fit_transform(documents)
    return vectorizer, dtm

def apply_lda(dtm, n_components=7):
    """
    Apply Latent Dirichlet Allocation
    
    Args:
        dtm: Document-term matrix
        n_components: Number of topics
        
    Returns:
        LDA model
    """
    lda = LatentDirichletAllocation(n_components=n_components, random_state=42)
    lda.fit(dtm)
    return lda

def train_predictive_model(dtm, topics):
    """
    Train Naive Bayes model
    
    Args:
        dtm: Document-term matrix
        topics: List of topics
        
    Returns:
        Trained model
    """
    nb = MultinomialNB()
    nb.fit(dtm, topics)
    return nb

def save_model_and_vectorizer(model, vectorizer):
    """
    Save model and vectorizer to disk
    
    Args:
        model: Trained model
        vectorizer: CountVectorizer
    """
    os.makedirs('database', exist_ok=True)
    with open('models/model.pkl', 'wb') as model_file:
        joblib.dump(model, model_file)
    with open('models/vectorizer.pkl', 'wb') as vectorizer_file:
        joblib.dump(vectorizer, vectorizer_file)

def process_csv(file_path):
    """
    Process CSV file for model training
    
    Args:
        file_path: Path to CSV file
    """
    df = read_csv(file_path)
    if df is None or not validate_columns(df, ['topic', 'link']):
        raise ValueError("Invalid CSV format")

    topics = df['topic'].tolist()
    links = df['link'].tolist()

    documents = scrape_documents(links)
    vectorizer, dtm = vectorize_documents(documents)
    lda = apply_lda(dtm)

    db.store_training_data(links, topics, documents, lda, vectorizer)
    nb_model = train_predictive_model(dtm, topics)
    save_model_and_vectorizer(nb_model, vectorizer)
    logger.info("CSV processed and data stored in MongoDB")

def backup_models():
    """
    Create backup of current models
    
    Returns:
        Backup timestamp or None if backup failed
    """
    backup_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        os.makedirs('database', exist_ok=True)
        if os.path.exists('models/vectorizer.pkl'):
            shutil.copy('models/vectorizer.pkl', f'database/vectorizer_{backup_time}.pkl')
        if os.path.exists('models/model.pkl'):
            shutil.copy('models/model.pkl', f'database/model_{backup_time}.pkl')
        logger.info(f"Created model backup with timestamp {backup_time}")
        return backup_time
    except Exception as e:
        logger.warning(f"Could not create model backup: {str(e)}")
        return None

def restore_models(backup_time):
    """
    Restore models from backup
    
    Args:
        backup_time: Backup timestamp
        
    Returns:
        True if restore succeeded, False otherwise
    """
    try:
        if os.path.exists(f'database/vectorizer_{backup_time}.pkl') and os.path.exists(f'database/model_{backup_time}.pkl'):
            shutil.copy(f'database/vectorizer_{backup_time}.pkl', 'models/vectorizer.pkl')
            shutil.copy(f'database/model_{backup_time}.pkl', 'models/model.pkl')
            logger.info("Restored model from backup")
            return True
    except Exception as e:
        logger.error(f"Error restoring model from backup: {str(e)}")
    return False

def retrain_model(urls, user_id):
    """
    Retrain model with new data
    
    Args:
        urls: List of URLs to use for retraining
        user_id: User ID
        
    Returns:
        Tuple of (success, message)
    """
    # Process each URL to get content
    contents = []
    topics = []
    
    for url in urls:
        # Check if we have this URL in history with a prediction
        history_entry = db.history_collection.find_one({"url": url, "user_id": user_id})
        if not history_entry:
            continue
            
        # Get content from cache or scrape
        cached_result = db.check_cache(url)
        if cached_result and 'text' in cached_result:
            content = cached_result['text']
        else:
            try:
                content = scrape_text_from_url(url)
                # Save to cache for future use
                db.save_to_cache(url, content, history_entry.get('prediction', ''))
            except Exception as e:
                logger.error(f"Error scraping URL {url}: {str(e)}")
                continue
        
        if content:
            contents.append(content)
            topics.append(history_entry.get('prediction', ''))
    
    if not contents:
        return False, "Could not retrieve content from any of the provided URLs"
    
    # Create backup of current model
    backup_time = backup_models()
    
    try:
        # Load current models
        vectorizer = joblib.load('models/vectorizer.pkl')
        model = joblib.load('models/model.pkl')
        
        # Vectorize the new content
        X = vectorizer.transform(contents)
        
        # Retrain the classifier with new data
        model.partial_fit(X, topics, classes=np.unique(topics))
        
        # Save updated models
        joblib.dump(vectorizer, 'models/vectorizer.pkl')
        joblib.dump(model, 'models/model.pkl')
        
        return True, f"Model successfully retrained with {len(contents)} documents"
    except Exception as e:
        logger.error(f"Error retraining model: {str(e)}")
        
        # Restore from backup if available
        if backup_time and restore_models(backup_time):
            return False, f"Error retraining model: {str(e)} (restored from backup)"
        else:
            return False, f"Error retraining model: {str(e)} (could not restore from backup)"

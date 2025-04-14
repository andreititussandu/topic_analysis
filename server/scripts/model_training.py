"""
Utilități pentru antrenarea modelului în aplicația de analiză a topicurilor
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

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inițializare bază de date
db = Database()

def read_csv(file_path):
    """
    Citește fișier CSV
    
    Args:
        file_path: Calea către fișierul CSV
        
    Returns:
        Pandas DataFrame sau None
    """
    try:
        df = pd.read_csv(file_path)
        logger.info("CSV citit cu succes")
        return df
    except Exception as e:
        logger.error(f"Eroare la citirea fișierului CSV: {e}")
        return None

def validate_columns(df, required_columns):
    """
    Validează coloanele necesare în DataFrame
    
    Args:
        df: Pandas DataFrame
        required_columns: Lista numelor coloanelor necesare
        
    Returns:
        True dacă toate coloanele necesare există, False în caz contrar
    """
    for column in required_columns:
        if column not in df.columns:
            logger.error(f"Eroare: Coloana necesară '{column}' nu a fost găsită în CSV")
            return False
    return True

def scrape_documents(links):
    """
    Extrage text din URL-uri
    
    Args:
        links: Lista de URL-uri
        
    Returns:
        Lista de documente text extrase
    """
    documents = []
    for link in links:
        try:
            logger.info(f"Extragere text din URL: {link}")
            text = scrape_text_from_url(link)
            documents.append(text)
        except Exception as e:
            logger.error(f"Eșec la extragerea {link}: {e}")
            documents.append('')
    return documents

def vectorize_documents(documents):
    """
    Vectorizează documente
    
    Args:
        documents: Lista de documente text
        
    Returns:
        Tuplu de (vectorizer, matrice document-termen)
    """
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english', ngram_range=(1, 2))
    dtm = vectorizer.fit_transform(documents)
    return vectorizer, dtm

def apply_lda(dtm, n_components=7):
    """
    Aplică Latent Dirichlet Allocation
    
    Args:
        dtm: Matricea document-termen
        n_components: Numărul de topicuri
        
    Returns:
        Modelul LDA
    """
    lda = LatentDirichletAllocation(n_components=n_components, random_state=42)
    lda.fit(dtm)
    return lda

def train_predictive_model(dtm, topics):
    """
    Antrenează modelul Naive Bayes
    
    Args:
        dtm: Matricea document-termen
        topics: Lista de topicuri
        
    Returns:
        Modelul antrenat
    """
    nb = MultinomialNB()
    nb.fit(dtm, topics)
    return nb

def save_model_and_vectorizer(model, vectorizer):
    """
    Salvează modelul și vectorizatorul pe disc
    
    Args:
        model: Modelul antrenat
        vectorizer: CountVectorizer
    """
    os.makedirs('database', exist_ok=True)
    with open('models/model.pkl', 'wb') as model_file:
        joblib.dump(model, model_file)
    with open('models/vectorizer.pkl', 'wb') as vectorizer_file:
        joblib.dump(vectorizer, vectorizer_file)

def process_csv(file_path):
    """
    Procesează fișierul CSV pentru antrenarea modelului
    
    Args:
        file_path: Calea către fișierul CSV
    """
    df = read_csv(file_path)
    if df is None or not validate_columns(df, ['topic', 'link']):
        raise ValueError("Format CSV invalid")

    topics = df['topic'].tolist()
    links = df['link'].tolist()

    documents = scrape_documents(links)
    vectorizer, dtm = vectorize_documents(documents)
    lda = apply_lda(dtm)

    db.store_training_data(links, topics, documents, lda, vectorizer)
    nb_model = train_predictive_model(dtm, topics)
    save_model_and_vectorizer(nb_model, vectorizer)
    logger.info("CSV procesat și datele stocate în MongoDB")

def backup_models():
    """
    Creează backup al modelelor curente
    
    Returns:
        Timestamp-ul backup-ului sau None dacă backup-ul a eșuat
    """
    backup_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        os.makedirs('database', exist_ok=True)
        if os.path.exists('models/vectorizer.pkl'):
            shutil.copy('models/vectorizer.pkl', f'database/vectorizer_{backup_time}.pkl')
        if os.path.exists('models/model.pkl'):
            shutil.copy('models/model.pkl', f'database/model_{backup_time}.pkl')
        logger.info(f"S-a creat backup-ul modelului cu timestamp-ul {backup_time}")
        return backup_time
    except Exception as e:
        logger.warning(f"Nu s-a putut crea backup-ul modelului: {str(e)}")
        return None

def restore_models(backup_time):
    """
    Restaurează modelele din backup
    
    Args:
        backup_time: Timestamp-ul backup-ului
        
    Returns:
        True dacă restaurarea a reușit, False în caz contrar
    """
    try:
        if os.path.exists(f'database/vectorizer_{backup_time}.pkl') and os.path.exists(f'database/model_{backup_time}.pkl'):
            shutil.copy(f'database/vectorizer_{backup_time}.pkl', 'models/vectorizer.pkl')
            shutil.copy(f'database/model_{backup_time}.pkl', 'models/model.pkl')
            logger.info("Model restaurat din backup")
            return True
    except Exception as e:
        logger.error(f"Eroare la restaurarea modelului din backup: {str(e)}")
    return False

def retrain_model(urls, user_id):
    """
    Reantrenează modelul cu date noi
    
    Args:
        urls: Lista de URL-uri pentru reantrenare
        user_id: ID-ul utilizatorului
        
    Returns:
        Tuplu de (succes, mesaj)
    """
    # Procesează fiecare URL pentru a obține conținutul
    contents = []
    topics = []
    
    for url in urls:
        # Verifică dacă avem acest URL în istoric cu o predicție
        history_entry = db.history_collection.find_one({"url": url, "user_id": user_id})
        if not history_entry:
            continue
            
        # Obține conținutul din cache sau prin extragere
        cached_result = db.check_cache(url)
        if cached_result and 'text' in cached_result:
            content = cached_result['text']
        else:
            try:
                content = scrape_text_from_url(url)
                # Salvează în cache pentru utilizare ulterioară
                db.save_to_cache(url, content, history_entry.get('prediction', ''))
            except Exception as e:
                logger.error(f"Eroare la extragerea URL-ului {url}: {str(e)}")
                continue
        
        if content:
            contents.append(content)
            topics.append(history_entry.get('prediction', ''))
    
    if not contents:
        return False, "Nu s-a putut recupera conținut din niciunul dintre URL-urile furnizate"
    
    # Creează backup al modelului curent
    backup_time = backup_models()
    
    try:
        # Încarcă modelele curente
        vectorizer = joblib.load('models/vectorizer.pkl')
        model = joblib.load('models/model.pkl')
        
        # Vectorizează noul conținut
        X = vectorizer.transform(contents)
        
        # Reantrenează clasificatorul cu noile date
        model.partial_fit(X, topics, classes=np.unique(topics))
        
        # Salvează modelele actualizate
        joblib.dump(vectorizer, 'models/vectorizer.pkl')
        joblib.dump(model, 'models/model.pkl')
        
        return True, f"Model reantrenat cu succes cu {len(contents)} documente"
    except Exception as e:
        logger.error(f"Eroare la reantrenarea modelului: {str(e)}")
        
        # Restaurează din backup dacă este disponibil
        if backup_time and restore_models(backup_time):
            return False, f"Eroare la reantrenarea modelului: {str(e)} (restaurat din backup)"
        else:
            return False, f"Eroare la reantrenarea modelului: {str(e)} (nu s-a putut restaura din backup)"

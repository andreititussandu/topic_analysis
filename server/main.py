from flask import request, jsonify, send_file
from flask_cors import cross_origin
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.naive_bayes import MultinomialNB
import pickle
import json
import os
import uuid
import datetime
from server.web_server import app, db, collection, history_collection, cache_collection
from scripts.web_scraper import scrape_text_from_url
#from scripts.summarizer import summarize_text
import shutil
import joblib
import numpy as np

# Function to read CSV file
def read_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print("CSV read successfully")
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

# Function to validate required columns
def validate_columns(df, required_columns):
    for column in required_columns:
        if column not in df.columns:
            print(f"Error: Required column '{column}' not found in CSV")
            return False
    return True

# Function to scrape text from URLs
def scrape_documents(links):
    documents = []
    for link in links:
        try:
            print(f"Scraping text from URL: {link}")
            text = scrape_text_from_url(link)
            documents.append(text)
        except Exception as e:
            print(f"Failed to scrape {link}: {e}")
            documents.append('')
    return documents

# Function to vectorize documents
def vectorize_documents(documents):
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english', ngram_range=(1, 2))
    dtm = vectorizer.fit_transform(documents)
    return vectorizer, dtm

# Function to apply LDA
def apply_lda(dtm, n_components=7):
    lda = LatentDirichletAllocation(n_components=n_components, random_state=42)
    lda.fit(dtm)
    return lda

# Function to store data in MongoDB
def store_in_mongodb(links, topics, documents, lda, vectorizer):
    for idx, link in enumerate(links):
        collection.insert_one({
            'url': link,
            'topic': topics[idx],
            'lda': lda.transform(vectorizer.transform([documents[idx]]))[0].tolist()
        })

# Function to train the Naive Bayes model
def train_predictive_model(dtm, topics):
    nb = MultinomialNB()
    nb.fit(dtm, topics)
    return nb

# Function to save models to disk
def save_model_and_vectorizer(model, vectorizer):
    with open('../models/model.pkl', 'wb') as model_file:
        pickle.dump(model, model_file)
    with open('../models/vectorizer.pkl', 'wb') as vectorizer_file:
        pickle.dump(vectorizer, vectorizer_file)

# Main function to process the CSV file
def process_csv(file_path):
    df = read_csv(file_path)
    if df is None or not validate_columns(df, ['topic', 'link']):
        return

    topics = df['topic'].tolist()
    links = df['link'].tolist()

    documents = scrape_documents(links)
    vectorizer, dtm = vectorize_documents(documents)
    lda = apply_lda(dtm)

    store_in_mongodb(links, topics, documents, lda, vectorizer)
    nb_model = train_predictive_model(dtm, topics)
    save_model_and_vectorizer(nb_model, vectorizer)
    print("CSV processed and data stored in MongoDB")

# Function to check cache for URL
def check_cache(url):
    cached_result = cache_collection.find_one({'url': url})
    if cached_result:
        # Check if cache is still valid (24 hours)
        cache_time = cached_result.get('timestamp', datetime.datetime.min)
        if (datetime.datetime.now() - cache_time).total_seconds() < 86400:  # 24 hours in seconds
            return cached_result
    return None

# Function to save to cache
def save_to_cache(url, text, prediction, word_frequencies=None):
    cache_collection.update_one(
        {'url': url},
        {'$set': {
            'url': url,
            'text': text,
            'prediction': prediction,
            'word_frequencies': word_frequencies,
            'timestamp': datetime.datetime.now()
        }},
        upsert=True
    )

# Function to save to history
def save_to_history(url, text, prediction, user_id=None, batch_id=None):
    history_collection.insert_one({
        'url': url,
        'text': text,
        'prediction': prediction,
        'timestamp': datetime.datetime.now(),
        'user_id': user_id,
        'batch_id': batch_id
    })

# Function to extract word frequencies for word cloud
def extract_word_frequencies(text):
    words = text.split()
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Only include words longer than 3 characters
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and take top 100 words
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
    return dict(sorted_words)

@app.route('/upload_csv', methods=['POST'])
@cross_origin()
def upload_csv():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        file_path = 'uploaded_file.csv'
        file.save(file_path)
        process_csv(file_path)
        return "CSV processed and data stored in MongoDB", 200
    else:
        return "No file uploaded", 400

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    url = request.json.get('url')
    user_id = request.json.get('user_id')
    
    if not url:
        return "No URL provided", 400

    # Check cache first
    cached_result = check_cache(url)
    if cached_result:
        # Save to history for tracking
        save_to_history(url, cached_result.get('text', ''), cached_result.get('prediction', ''), user_id)
        return jsonify({
            'predicted_topic': cached_result.get('prediction', ''),
            'word_frequencies': cached_result.get('word_frequencies', {}),
            'from_cache': True
        }), 200

    try:
        text = scrape_text_from_url(url)
    except Exception as e:
        return f"Failed to scrape {url}: {e}", 500

    with open('./models/model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('./models/vectorizer.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)

    text_vectorized = vectorizer.transform([text])
    prediction = model.predict(text_vectorized)[0]
    
    # Extract word frequencies for word cloud
    word_frequencies = extract_word_frequencies(text)
    
    # Save to cache
    save_to_cache(url, text, prediction, word_frequencies)
    
    # Save to history
    save_to_history(url, text, prediction, user_id)

    return jsonify({
        'predicted_topic': prediction,
        'word_frequencies': word_frequencies,
        'from_cache': False
    }), 200

@app.route('/batch_predict', methods=['POST'])
@cross_origin()
def batch_predict():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if file.filename == '':
        return "No selected file", 400

    if file:
        try:
            # Generate a batch ID for grouping
            batch_id = str(uuid.uuid4())
            
            # Read URLs from the text file
            content = file.read().decode('utf-8')
            urls = [url.strip() for url in content.split('\n') if url.strip()]
            
            results = []
            for url in urls:
                if not url:
                    continue
                    
                # Check cache first
                cached_result = check_cache(url)
                if cached_result:
                    results.append({
                        'url': url,
                        'predicted_topic': cached_result.get('prediction', ''),
                        'from_cache': True
                    })
                    save_to_history(url, cached_result.get('text', ''), cached_result.get('prediction', ''), user_id, batch_id)
                    continue
                
                try:
                    text = scrape_text_from_url(url)
                    
                    with open('./models/model.pkl', 'rb') as model_file:
                        model = pickle.load(model_file)
                    with open('./models/vectorizer.pkl', 'rb') as vectorizer_file:
                        vectorizer = pickle.load(vectorizer_file)
                    
                    text_vectorized = vectorizer.transform([text])
                    prediction = model.predict(text_vectorized)[0]
                    
                    # Extract word frequencies
                    word_frequencies = extract_word_frequencies(text)
                    
                    # Save to cache
                    save_to_cache(url, text, prediction, word_frequencies)
                    
                    # Save to history
                    save_to_history(url, text, prediction, user_id, batch_id)
                    
                    results.append({
                        'url': url,
                        'predicted_topic': prediction,
                        'from_cache': False
                    })
                except Exception as e:
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
            
            return jsonify({
                'results': results,
                'grouped_results': grouped_results,
                'batch_id': batch_id
            }), 200
            
        except Exception as e:
            return f"Error processing batch: {str(e)}", 500
    else:
        return "No file uploaded", 400

@app.route('/save_content', methods=['POST'])
@cross_origin()
def save_content():
    url = request.json.get('url')
    user_id = request.json.get('user_id')
    
    if not url:
        return "No URL provided", 400
    
    try:
        # Check if we have it in cache first
        cached_result = check_cache(url)
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
        
        return jsonify({
            'message': 'Content saved successfully',
            'filename': filename,
            'filepath': filepath
        }), 200
        
    except Exception as e:
        return f"Error saving content: {str(e)}", 500

@app.route('/download_content/<path:filename>', methods=['GET'])
@cross_origin()
def download_content(filename):
    try:
        # Ensure the filename is safe
        safe_filename = os.path.basename(filename)
        filepath = os.path.join('saved_content', safe_filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return "File not found", 404
            
        return send_file(filepath, as_attachment=True, download_name=safe_filename)
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/history', methods=['GET'])
@cross_origin()
def get_history():
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    query = {}
    if user_id:
        query['user_id'] = user_id
    
    history = list(history_collection.find(
        query, 
        {'_id': 0, 'url': 1, 'prediction': 1, 'timestamp': 1, 'batch_id': 1}
    ).sort('timestamp', -1).limit(limit))
    
    # Convert timestamp to string for JSON serialization
    for item in history:
        if 'timestamp' in item:
            item['timestamp'] = item['timestamp'].isoformat()
    
    return jsonify(history), 200

@app.route('/analytics', methods=['GET'])
@cross_origin()
def get_analytics():
    user_id = request.args.get('user_id')
    
    query = {}
    if user_id:
        query['user_id'] = user_id
    
    # Get topic distribution
    pipeline = [
        {'$match': query},
        {'$group': {'_id': '$prediction', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    
    topic_distribution = list(history_collection.aggregate(pipeline))
    
    # Get recent activity (last 7 days)
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    
    daily_activity_query = query.copy()
    daily_activity_query['timestamp'] = {'$gte': seven_days_ago}
    
    daily_activity_pipeline = [
        {'$match': daily_activity_query},
        {'$group': {
            '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]
    
    daily_activity = list(history_collection.aggregate(daily_activity_pipeline))
    
    return jsonify({
        'topic_distribution': topic_distribution,
        'daily_activity': daily_activity
    }), 200

@app.route('/retrain_model', methods=['POST'])
@cross_origin()
def retrain_model():
    """
    Retrain the topic prediction model using selected URLs from history.
    
    Request JSON format:
    {
        "urls": ["url1", "url2", ...],
        "user_id": "user_id"
    }
    
    Returns:
    {
        "success": true/false,
        "message": "Success/error message"
    }
    """
    try:
        data = request.json
        urls = data.get('urls', [])
        user_id = data.get('user_id', '')
        
        if not urls:
            return jsonify({"success": False, "message": "No URLs provided for retraining"}), 400
        
        # Log retraining request
        app.logger.info(f"Retraining model with {len(urls)} URLs for user {user_id}")
        
        # Process each URL to get content
        contents = []
        topics = []
        
        for url in urls:
            # Check if we have this URL in history with a prediction
            history_entry = history_collection.find_one({"url": url, "user_id": user_id})
            if not history_entry:
                continue
                
            # Get content from cache or scrape
            cached_result = check_cache(url)
            if cached_result and 'text' in cached_result:
                content = cached_result['text']
            else:
                try:
                    content = scrape_text_from_url(url)
                    # Save to cache for future use
                    save_to_cache(url, content, history_entry.get('prediction', ''))
                except Exception as e:
                    app.logger.error(f"Error scraping URL {url}: {str(e)}")
                    continue
            
            if content:
                contents.append(content)
                topics.append(history_entry.get('prediction', ''))
        
        if not contents:
            return jsonify({"success": False, "message": "Could not retrieve content from any of the provided URLs"}), 400
        
        # Create backup of current model
        backup_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        try:
            shutil.copy('models/vectorizer.pkl', f'models/vectorizer_{backup_time}.pkl')
            shutil.copy('models/classifier.pkl', f'models/classifier_{backup_time}.pkl')
            app.logger.info(f"Created model backup with timestamp {backup_time}")
        except Exception as e:
            app.logger.warning(f"Could not create model backup: {str(e)}")
        
        try:
            # Load current models
            vectorizer = joblib.load('models/vectorizer.pkl')
            classifier = joblib.load('models/classifier.pkl')
            
            # Vectorize the new content
            X = vectorizer.transform(contents)
            
            # Retrain the classifier with new data
            classifier.partial_fit(X, topics, classes=np.unique(topics))
            
            # Save updated models
            joblib.dump(vectorizer, 'models/vectorizer.pkl')
            joblib.dump(classifier, 'models/classifier.pkl')
            
            return jsonify({
                "success": True, 
                "message": f"Model successfully retrained with {len(contents)} documents"
            })
        except Exception as e:
            app.logger.error(f"Error retraining model: {str(e)}")
            
            # Restore from backup if available
            try:
                if os.path.exists(f'models/vectorizer_{backup_time}.pkl') and os.path.exists(f'models/classifier_{backup_time}.pkl'):
                    shutil.copy(f'models/vectorizer_{backup_time}.pkl', 'models/vectorizer.pkl')
                    shutil.copy(f'models/classifier_{backup_time}.pkl', 'models/classifier.pkl')
                    app.logger.info("Restored model from backup after retraining failure")
            except Exception as restore_error:
                app.logger.error(f"Error restoring model from backup: {str(restore_error)}")
            
            return jsonify({"success": False, "message": f"Error retraining model: {str(e)}"}), 500
    
    except Exception as e:
        app.logger.error(f"Error in retrain_model: {str(e)}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False)

# be - gunicorn -c gunicorn_config.py server.main:app
# fe - npm start
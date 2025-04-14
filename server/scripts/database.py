"""
Operațiuni de bază de date pentru aplicația de analiză a topicurilor
"""
import datetime
from pymongo import MongoClient
import os

class Database:
    def __init__(self, mongo_uri=None):
        """
        Inițializează conexiunea la baza de date
        
        Args:
            mongo_uri: String de conexiune MongoDB
        """
        self.mongo_uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client['web_topic_modeling']
        self.collection = self.db['webpages']
        self.history_collection = self.db['history']
        self.cache_collection = self.db['cache']
        
        # Creează indexuri pentru performanță mai bună
        self.history_collection.create_index([('url', 1)])
        self.history_collection.create_index([('user_id', 1)])
        self.history_collection.create_index([('timestamp', -1)])
        self.history_collection.create_index([('batch_id', 1)])
        
        self.cache_collection.create_index([('url', 1)], unique=True)
        self.cache_collection.create_index([('timestamp', 1)])
    
    def check_cache(self, url):
        """
        Verifică dacă URL-ul este în cache
        
        Args:
            url: URL-ul de verificat
            
        Returns:
            Rezultatul din cache sau None
        """
        cached_result = self.cache_collection.find_one({'url': url})
        if cached_result:
            # Verifică dacă cache-ul este încă valid (24 ore)
            cache_time = cached_result.get('timestamp', datetime.datetime.min)
            if (datetime.datetime.now() - cache_time).total_seconds() < 86400:  # 24 hours in seconds
                return cached_result
        return None
    
    def save_to_cache(self, url, text, prediction, word_frequencies=None):
        """
        Save to cache
        
        Args:
            url: URL to save
            text: Text content
            prediction: Predicted topic
            word_frequencies: Word frequencies for word cloud
        """
        self.cache_collection.update_one(
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
    
    def save_to_history(self, url, text, prediction, user_id=None, batch_id=None):
        """
        Save to history
        
        Args:
            url: URL to save
            text: Text content
            prediction: Predicted topic
            user_id: User ID
            batch_id: Batch ID for grouping
        """
        self.history_collection.insert_one({
            'url': url,
            'text': text,
            'prediction': prediction,
            'timestamp': datetime.datetime.now(),
            'user_id': user_id,
            'batch_id': batch_id
        })
    
    def get_history(self, user_id=None, limit=50):
        """
        Get history
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List of history records
        """
        query = {}
        if user_id:
            query['user_id'] = user_id
        
        history = list(self.history_collection.find(
            query, 
            {'_id': 0, 'url': 1, 'prediction': 1, 'timestamp': 1, 'batch_id': 1}
        ).sort('timestamp', -1).limit(limit))
        
        # Convert timestamp to string for JSON serialization
        for item in history:
            if 'timestamp' in item:
                item['timestamp'] = item['timestamp'].isoformat()
        
        return history
    
    def get_analytics(self, user_id=None, days=7):
        """
        Get analytics
        
        Args:
            user_id: User ID
            days: Number of days to include
            
        Returns:
            Dictionary with analytics data
        """
        query = {}
        if user_id:
            query['user_id'] = user_id
        
        # Get topic distribution
        pipeline = [
            {'$match': query},
            {'$group': {'_id': '$prediction', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        topic_distribution = list(self.history_collection.aggregate(pipeline))
        
        # Get recent activity
        days_ago = datetime.datetime.now() - datetime.timedelta(days=days)
        
        daily_activity_query = query.copy()
        daily_activity_query['timestamp'] = {'$gte': days_ago}
        
        daily_activity_pipeline = [
            {'$match': daily_activity_query},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        daily_activity = list(self.history_collection.aggregate(daily_activity_pipeline))
        
        return {
            'topic_distribution': topic_distribution,
            'daily_activity': daily_activity
        }
    
    def store_training_data(self, links, topics, documents, lda, vectorizer):
        """
        Store training data in MongoDB
        
        Args:
            links: List of URLs
            topics: List of topics
            documents: List of documents
            lda: LDA model
            vectorizer: CountVectorizer
        """
        for idx, link in enumerate(links):
            self.collection.insert_one({
                'url': link,
                'topic': topics[idx],
                'lda': lda.transform(vectorizer.transform([documents[idx]]))[0].tolist()
            })

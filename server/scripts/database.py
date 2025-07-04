import datetime
from pymongo import MongoClient
import os

class Database:
    def __init__(self, mongo_uri=None):
        # Inițializează conexiunea la baza de date
        self.mongo_uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client['web_topic_modeling']
        self.collection = self.db['webpages']
        self.history_collection = self.db['history']
        self.cache_collection = self.db['cache']
        
        # Creează indexuri
        self.history_collection.create_index([('url', 1)])
        self.history_collection.create_index([('user_id', 1)])
        self.history_collection.create_index([('timestamp', -1)])
        self.history_collection.create_index([('batch_id', 1)])
        
        self.cache_collection.create_index([('url', 1)], unique=True)
        self.cache_collection.create_index([('timestamp', 1)])
    
    def check_cache(self, url):
        # Verifică dacă pagina este în cache
        cached_result = self.cache_collection.find_one({'url': url})
        if cached_result:
            cache_time = cached_result.get('timestamp', datetime.datetime.min)
            if (datetime.datetime.now() - cache_time).total_seconds() < 86400:  # 24 de ore în secunde
                return cached_result
        return None
    
    def save_to_cache(self, url, text, prediction, word_frequencies=None):
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
        self.history_collection.insert_one({
            'url': url,
            'text': text,
            'prediction': prediction,
            'timestamp': datetime.datetime.now(),
            'user_id': user_id,
            'batch_id': batch_id
        })
    
    def get_history(self, user_id=None, limit=50):
        query = {}
        if user_id:
            query['user_id'] = user_id
        
        # Se convertesc variabilele în string pentru a putea fi serializat în JSON
        history = []
        cursor = self.history_collection.find(query).sort('timestamp', -1).limit(limit)
        
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            history.append(doc)

        for item in history:
            if 'timestamp' in item:
                item['timestamp'] = item['timestamp'].isoformat()
        
        return history
    
    def get_analytics(self, user_id=None, days=7):
        pipeline = []
        
        # Adăugăm filtru pentru perioada de timp premergătoare actiunii
        date_limit = datetime.datetime.now() - datetime.timedelta(days=days)
        pipeline.append({'$match': {'timestamp': {'$gte': date_limit}}})
        
        # Filtrare după user_id dacă este specificat
        if user_id:
            pipeline.append({'$match': {'user_id': user_id}})

        topic_pipeline = pipeline + [
            {'$group': {'_id': '$prediction', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]

        daily_pipeline = pipeline + [
            {'$project': {
                'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
            }},
            {'$group': {'_id': '$date', 'count': {'$sum': 1}}},
            {'$sort': {'_id': -1}},
            {'$limit': 7}
        ]

        topic_distribution = list(self.history_collection.aggregate(topic_pipeline))
        daily_activity = list(self.history_collection.aggregate(daily_pipeline))
        
        return {
            'topic_distribution': topic_distribution,
            'daily_activity': daily_activity
        }
        
    def delete_history_entry(self, entry_id, user_id=None):
        from bson.objectid import ObjectId
        
        try:
            query = {'_id': ObjectId(entry_id)}

            if user_id:
                query['user_id'] = user_id

            result = self.history_collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Eroare la ștergerea intrării din istoric: {str(e)}")
            return False
    
    def store_training_data(self, links, topics, documents, lda, vectorizer):
        for idx, link in enumerate(links):
            self.collection.insert_one({
                'url': link,
                'topic': topics[idx],
                'lda': lda.transform(vectorizer.transform([documents[idx]]))[0].tolist()
            })

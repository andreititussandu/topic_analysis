from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import os

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

client = MongoClient(MONGO_URI)
db = client['web_topic_modeling']
collection = db['webpages']
history_collection = db['history']
cache_collection = db['cache']

# Create indexes for better performance
history_collection.create_index([('url', 1)])
history_collection.create_index([('user_id', 1)])
history_collection.create_index([('timestamp', -1)])
history_collection.create_index([('batch_id', 1)])

cache_collection.create_index([('url', 1)], unique=True)
cache_collection.create_index([('timestamp', 1)])

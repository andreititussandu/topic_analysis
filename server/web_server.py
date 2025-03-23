from flask import Flask
from flask_cors import CORS
import os

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

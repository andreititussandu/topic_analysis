from flask import request, jsonify, send_file
from flask_cors import cross_origin
import os

# Import from scripts modules
from server.scripts.database import Database
from server.scripts.prediction import predict_topic, batch_predict
from server.scripts.model_training import process_csv, retrain_model
from server.scripts.content_management import save_content, get_file_path

# Import server configuration
from server.web_server import app

# Initialize database
db = Database()

@app.route('/upload_csv', methods=['POST'])
@cross_origin()
def upload_csv():
    """
    Upload CSV file for model training
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            file_path = 'uploaded_file.csv'
            file.save(file_path)
            process_csv(file_path)
            return jsonify({"message": "CSV processed and data stored in MongoDB"}), 200
        except Exception as e:
            app.logger.error(f"Error processing CSV: {str(e)}")
            return jsonify({"error": f"Error processing CSV: {str(e)}"}), 500
    else:
        return jsonify({"error": "No file uploaded"}), 400

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    """
    Predict topic for a URL
    """
    url = request.json.get('url')
    user_id = request.json.get('user_id')
    
    result, status_code = predict_topic(url, user_id)
    return jsonify(result), status_code

@app.route('/batch_predict', methods=['POST'])
@cross_origin()
def batch_predict_route():
    """
    Predict topics for multiple URLs
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            # Read URLs from the text file
            content = file.read().decode('utf-8')
            urls = [url.strip() for url in content.split('\n') if url.strip()]
            
            result, status_code = batch_predict(urls, user_id)
            return jsonify(result), status_code
        except Exception as e:
            app.logger.error(f"Error processing batch: {str(e)}")
            return jsonify({"error": f"Error processing batch: {str(e)}"}), 500
    else:
        return jsonify({"error": "No file uploaded"}), 400

@app.route('/save_content', methods=['POST'])
@cross_origin()
def save_content_route():
    """
    Save content from URL to file
    """
    url = request.json.get('url')
    user_id = request.json.get('user_id')
    
    result, status_code = save_content(url, user_id)
    return jsonify(result), status_code

@app.route('/download_content/<path:filename>', methods=['GET'])
@cross_origin()
def download_content(filename):
    """
    Download saved content
    """
    filepath, error, status_code = get_file_path(filename)
    
    if error:
        return jsonify({"error": error}), status_code
    
    return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))

@app.route('/history', methods=['GET'])
@cross_origin()
def get_history():
    """
    Get user prediction history
    """
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    history = db.get_history(user_id, limit)
    return jsonify(history), 200

@app.route('/analytics', methods=['GET'])
@cross_origin()
def get_analytics():
    """
    Get analytics data
    """
    user_id = request.args.get('user_id')
    days = int(request.args.get('days', 7))
    
    analytics = db.get_analytics(user_id, days)
    return jsonify(analytics), 200

@app.route('/retrain_model', methods=['POST'])
@cross_origin()
def retrain_model_route():
    """
    Retrain the topic prediction model using selected URLs from history
    """
    try:
        data = request.json
        urls = data.get('urls', [])
        user_id = data.get('user_id', '')
        
        if not urls:
            return jsonify({"success": False, "message": "No URLs provided for retraining"}), 400
        
        # Log retraining request
        app.logger.info(f"Retraining model with {len(urls)} URLs for user {user_id}")
        
        success, message = retrain_model(urls, user_id)
        return jsonify({"success": success, "message": message}), 200 if success else 500
    
    except Exception as e:
        app.logger.error(f"Error in retrain_model: {str(e)}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False)

# be - gunicorn -c gunicorn_config.py server.main:app
# fe - npm start
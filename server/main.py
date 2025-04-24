from flask import request, jsonify, send_file
from flask_cors import cross_origin
import os

# Import din modulele scripts
from server.scripts.database import Database
from server.scripts.prediction import predict_topic, batch_predict
from server.scripts.model_training import process_csv, retrain_model
from server.scripts.content_management import save_content, get_file_path

# Import configurație server
from server.web_server import app

# Inițializare bază de date
db = Database()

@app.route('/upload_csv', methods=['POST'])
@cross_origin()
def upload_csv():
    """
    Încarcă fișier CSV pentru antrenarea modelului
    """
    if 'file' not in request.files:
        return jsonify({"error": "Nu există partea de fișier în cerere"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Niciun fișier selectat"}), 400

    if file:
        try:
            file_path = 'uploaded_file.csv'
            file.save(file_path)
            process_csv(file_path)
            return jsonify({"message": "CSV procesat și datele stocate în MongoDB"}), 200
        except Exception as e:
            app.logger.error(f"Eroare la procesarea CSV: {str(e)}")
            return jsonify({"error": f"Eroare la procesarea CSV: {str(e)}"}), 500
    else:
        return jsonify({"error": "Niciun fișier încărcat"}), 400

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    """
    Prezice topicul pentru un URL
    """
    url = request.json.get('url')
    user_id = request.json.get('user_id')
    
    result, status_code = predict_topic(url, user_id)
    return jsonify(result), status_code

@app.route('/batch_predict', methods=['POST'])
@cross_origin()
def batch_predict_route():
    """
    Prezice topicuri pentru mai multe URL-uri
    """
    if 'file' not in request.files:
        return jsonify({"error": "Nu există partea de fișier în cerere"}), 400

    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if file.filename == '':
        return jsonify({"error": "Niciun fișier selectat"}), 400

    if file:
        try:
            # Citește URL-urile din fișierul text
            content = file.read().decode('utf-8')
            urls = [url.strip() for url in content.split('\n') if url.strip()]
            
            result, status_code = batch_predict(urls, user_id)
            return jsonify(result), status_code
        except Exception as e:
            app.logger.error(f"Eroare la procesarea lotului: {str(e)}")
            return jsonify({"error": f"Eroare la procesarea lotului: {str(e)}"}), 500
    else:
        return jsonify({"error": "Niciun fișier încărcat"}), 400

@app.route('/save_content', methods=['POST'])
@cross_origin()
def save_content_route():
    """
    Salvează conținutul din URL în fișier
    """
    url = request.json.get('url')
    user_id = request.json.get('user_id')
    
    result, status_code = save_content(url, user_id)
    return jsonify(result), status_code

@app.route('/download_content/<path:filename>', methods=['GET'])
@cross_origin()
def download_content(filename):
    """
    Descarcă conținutul salvat
    """
    filepath, error, status_code = get_file_path(filename)
    
    if error:
        return jsonify({"error": error}), status_code
    
    return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))

@app.route('/history', methods=['GET'])
@cross_origin()
def get_history():
    """
    Obține istoricul predicțiilor utilizatorului
    """
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    history = db.get_history(user_id, limit)
    return jsonify(history), 200


@app.route('/history/<entry_id>', methods=['DELETE'])
@cross_origin()
def delete_history_entry(entry_id):
    """
    Șterge o intrare din istoricul predicțiilor
    """
    user_id = request.args.get('user_id')

    if not entry_id:
        return jsonify({"error": "ID-ul intrării nu a fost specificat"}), 400

    try:
        success = db.delete_history_entry(entry_id, user_id)
        if success:
            return jsonify({"success": True, "message": "Intrarea a fost ștearsă cu succes"}), 200
        else:
            return jsonify({"success": False, "message": "Intrarea nu a fost găsită sau nu poate fi ștearsă"}), 404
    except Exception as e:
        app.logger.error(f"Eroare la ștergerea intrării: {str(e)}")
        return jsonify({"success": False, "message": f"Eroare la ștergerea intrării: {str(e)}"}), 500

@app.route('/analytics', methods=['GET'])
@cross_origin()
def get_analytics():
    """
    Obține date analitice
    """
    user_id = request.args.get('user_id')
    days = int(request.args.get('days', 7))
    
    analytics = db.get_analytics(user_id, days)
    return jsonify(analytics), 200

@app.route('/retrain_model', methods=['POST'])
@cross_origin()
def retrain_model_route():
    """
    Reantrenează modelul de predicție a topicurilor folosind URL-urile selectate din istoric
    """
    try:
        data = request.json
        urls = data.get('urls', [])
        user_id = data.get('user_id', '')
        
        if not urls:
            return jsonify({"success": False, "message": "Nu au fost furnizate URL-uri pentru reantrenare"}), 400
        
        # Înregistrează cererea de reantrenare
        app.logger.info(f"Reantrenarea modelului cu {len(urls)} URL-uri pentru utilizatorul {user_id}")
        
        success, message = retrain_model(urls, user_id)
        return jsonify({"success": success, "message": message}), 200 if success else 500
    
    except Exception as e:
        app.logger.error(f"Eroare în retrain_model: {str(e)}")
        return jsonify({"success": False, "message": f"Eroare de server: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=False)

# backend - gunicorn -c gunicorn_config.py server.main:app
# frontend - npm start
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'photos' not in request.files:
        return "No file part", 400

    files = request.files.getlist('photos')
    saved_files = []

    for file in files:
        if file.filename == '':
            continue
        filename = secure_filename(f"{int(time.time())}-{file.filename}")
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        saved_files.append({
            'filename': filename,
            'url': f"/uploads/{filename}"
        })

    return jsonify({
        'message': '✅ Uploaded successfully!',
        'files': saved_files
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os
import time  # 👈 for timestamp to avoid overwrite

app = Flask(__name__)
CORS(app)

# 🔐 Cloudinary Configuration
cloudinary.config(
    cloud_name="dx1jvytp4",                 # <-- Apna cloud name
    api_key="932781884527291",             # <-- Apna API key
    api_secret="eRSeF486FPV-eh8YpBWZX8wJe7c"  # <-- Apna API secret
)

@app.route('/')
def home():
    return '📸 SnapBox Cloudinary Backend is Live!'

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'photos' not in request.files:
        return "No file part", 400

    files = request.files.getlist('photos')
    uploaded_urls = []

    for index, file in enumerate(files):
        if file.filename == '':
            continue

        # 🕒 Unique timestamp for each image name
        timestamp = int(time.time())

        # 📤 Upload to Cloudinary in 'snapbox' folder with unique name
        result = cloudinary.uploader.upload(
            file,
            public_id=f"snapbox/selfie_{timestamp}_{index + 1}",  # 👈 unique name inside folder
            overwrite=False,
            resource_type="image"
        )

        # ✅ Save secure URL
        uploaded_urls.append(result['secure_url'])

    return jsonify({
        'message': '✅ Uploaded Permanently to Cloudinary!',
        'urls': uploaded_urls
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

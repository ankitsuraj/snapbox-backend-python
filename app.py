from flask import Flask, request, jsonify from flask_cors import CORS import cloudinary import cloudinary.uploader import os

app = Flask(name) CORS(app)

Cloudinary Configuration

cloudinary.config( cloud_name = "dx1jvytp4",           # ✅ Your Cloud Name api_key = "932781884527291",       # ✅ Your API Key api_secret = "eRSeF486FPV-eh8YpBWZX8wJe7c"  # ✅ Your API Secret )

@app.route('/') def home(): return '📸 SnapBox Cloudinary Backend is Live!'

@app.route('/upload', methods=['POST']) def upload_files(): if 'photos' not in request.files: return "No file part", 400

files = request.files.getlist('photos')
uploaded_urls = []

for index, file in enumerate(files):
    if file.filename == '':
        continue
    # Uploading to Cloudinary inside 'snapbox/' folder
    result = cloudinary.uploader.upload(
        file,
        folder="snapbox",
        public_id=f"selfie_{index + 1}",
        overwrite=True
    )
    uploaded_urls.append(result['secure_url'])

return jsonify({
    'message': '✅ Uploaded to Cloudinary!',
    'urls': uploaded_urls
})

if name == 'main': port = int(os.environ.get("PORT", 5000)) app.run(debug=True, host='0.0.0.0', port=port)


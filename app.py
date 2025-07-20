from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import cloudinary.api
import time
import os

app = Flask(__name__)
CORS(app)

# Cloudinary Config
cloudinary.config(
    cloud_name="dx1jvytp4",
    api_key="932781884527291",
    api_secret="eRSeF486FPV-eh8YpBWZX8wJe7c"
)

@app.route('/')
def home():
    try:
        # ✅ Force fresh fetch using `next_cursor` and max results
        result = cloudinary.Search() \
            .expression("folder:snapbox") \
            .sort_by("created_at", "desc") \
            .max_results(30) \
            .execute()

        image_urls = [item['secure_url'] for item in result['resources']]

        # Render Image Gallery
        html = '<h2>📸 SnapBox Cloudinary Backend is Live!</h2>'
        html += '<h3>🖼️ Uploaded Selfies:</h3><div style="display:flex;flex-wrap:wrap;gap:10px;">'

        for url in image_urls:
            html += f'<div><img src="{url}" width="200" style="border-radius:10px;"></div>'

        html += '</div>'
        return html

    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'photos' not in request.files:
        return "No file part", 400

    files = request.files.getlist('photos')
    uploaded_urls = []

    for index, file in enumerate(files):
        if file.filename == '':
            continue

        timestamp = int(time.time())
        result = cloudinary.uploader.upload(
            file,
            public_id=f"snapbox/selfie_{timestamp}_{index + 1}",
            overwrite=False,
            invalidate=True,  # ✅ Add this to avoid CDN delay
            resource_type="image"
        )
        uploaded_urls.append(result['secure_url'])

    return jsonify({
        'message': '✅ Uploaded to Cloudinary!',
        'urls': uploaded_urls
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

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
        # 🔄 Get latest 20 selfies from snapbox folder
        result = cloudinary.Search() \
            .expression("folder:snapbox") \
            .sort_by("created_at", "desc") \
            .max_results(20) \
            .execute()

        image_urls = [item['secure_url'] for item in result['resources']]

        # 🖼️ HTML render
        html = '''
        <h2 style="font-family:sans-serif;">📸 SnapBox Cloudinary Backend is Live!</h2>
        <p>Showing latest uploaded selfies:</p>
        <div style="display:flex;flex-wrap:wrap;gap:10px;">
        '''

        for url in image_urls:
            html += f'<div><img src="{url}" width="200" style="border-radius:10px;border:1px solid #ccc;"></div>'

        html += '</div>'
        return html

    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"

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
            invalidate=True,  # ✅ Important for latest version to show
            resource_type="image"
        )
        uploaded_urls.append(result['secure_url'])

    return jsonify({
        'message': '✅ Uploaded to Cloudinary!',
        'urls': uploaded_urls
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import cloudinary.api
import time
import os
import random

app = Flask(__name__)
CORS(app)

# 🔐 Cloudinary Config
cloudinary.config(
    cloud_name="dx1jvytp4",
    api_key="932781884527291",
    api_secret="eRSeF486FPV-eh8YpBWZX8wJe7c"
)

@app.route('/')
def home():
    try:
        result = cloudinary.Search() \
            .expression("folder:snapbox AND resource_type:image") \
            .sort_by("created_at", "desc") \
            .max_results(100) \
            .execute()

        resources = result['resources']

        # ⏱ Group by upload session (60 sec threshold)
        grouped = []
        current_group = []
        last_time = None
        threshold = 60  # seconds between grouped uploads

        for item in resources:
            created_at = item['created_at']
            timestamp = int(time.mktime(time.strptime(created_at[:19], "%Y-%m-%dT%H:%M:%S")))

            if last_time is None or abs(last_time - timestamp) <= threshold:
                current_group.append(item['secure_url'])
            else:
                grouped.append(current_group)
                current_group = [item['secure_url']]

            last_time = timestamp

        if current_group:
            grouped.append(current_group)

        # 📄 Generate HTML
        html = '''
        <h2 style="font-family:sans-serif;">📸 SnapBox Cloudinary Backend is Live!</h2>
        <div style="font-family:monospace; font-size:14px;">
        '''

        for i, group in enumerate(grouped, start=1):
            html += f"<p><b>{i}. Images</b></p>"
            for url in group:
                html += f'''
                <div style="margin-bottom:6px;">
                    {url}
                    <a href="{url}" target="_blank" style="margin-left:10px; padding:2px 6px; background:#333; color:#fff; text-decoration:none; border-radius:4px;">Open</a>
                </div>
                '''
            html += "<br>"

        html += "</div>"
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
        unique_id = random.randint(1000, 9999)
        result = cloudinary.uploader.upload(
            file,
            public_id=f"snapbox/selfie_{timestamp}_{index + 1}_{unique_id}",
            overwrite=False,
            invalidate=True,
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

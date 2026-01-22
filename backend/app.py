import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from compression import compress_file

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
COMPRESSED_FOLDER = os.path.join(os.path.dirname(__file__), 'compressed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER
# No limit on upload size. By default, Flask allows any size if MAX_CONTENT_LENGTH is None.
app.config['MAX_CONTENT_LENGTH'] = None 

# Store file info in memory (for a production app, use a database or redis)
files_db = {}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
    file.save(file_path)
    
    original_size = os.path.getsize(file_path)
    files_db[file_id] = {
        'original_filename': filename,
        'original_path': file_path,
        'original_size': original_size,
        'extension': filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    }
    
    return jsonify({
        'file_id': file_id,
        'filename': filename,
        'size': original_size
    })

@app.route('/api/compress', methods=['POST'])
def compress_endpoint():
    data = request.json
    file_id = data.get('file_id')
    quality = int(data.get('quality', 70))
    
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    file_info = files_db[file_id]
    original_path = file_info['original_path']
    compressed_filename = f"compressed_{file_info['original_filename']}"
    compressed_path = os.path.join(app.config['COMPRESSED_FOLDER'], f"{file_id}_{compressed_filename}")
    
    try:
        compress_file(original_path, compressed_path, quality, file_info['extension'])
        compressed_size = os.path.getsize(compressed_path)
        reduction = ((file_info['original_size'] - compressed_size) / file_info['original_size']) * 100
        
        file_info['compressed_path'] = compressed_path
        file_info['compressed_size'] = compressed_size
        
        return jsonify({
            'file_id': file_id,
            'original_size': file_info['original_size'],
            'compressed_size': compressed_size,
            'reduction_percentage': round(reduction, 2),
            'download_url': url_for('download_file', file_id=file_id, _external=True)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    if file_id not in files_db or 'compressed_path' not in files_db[file_id]:
        return jsonify({'error': 'Compressed file not found'}), 404
    
    file_info = files_db[file_id]
    directory = app.config['COMPRESSED_FOLDER']
    filename = os.path.basename(file_info['compressed_path'])
    
    return send_from_directory(directory, filename, as_attachment=True, download_name=file_info['original_filename'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

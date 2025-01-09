from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from utils.auth import login_required
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)
upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = '/data/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('', methods=['POST'])
@upload_bp.route('/', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_path = os.path.join(UPLOAD_FOLDER, timestamp)
        os.makedirs(upload_path, exist_ok=True)

        image_filename = secure_filename(file.filename)
        image_path = os.path.join(upload_path, image_filename)
        file.save(image_path)

        base_url = "https://cryptoplace.kusmicrew.cloud"

        relative_image_path = f"{base_url}/api/uploads/{timestamp}/{image_filename}"
        relative_metadata_path = f"{base_url}/api/uploads/{timestamp}/metadata.json"

        public_image_url = f"{base_url}/api/uploads/{timestamp}/{image_filename}"

        metadata = {
            "name": request.form.get('title', image_filename),
            "description": request.form.get('description', ''),
            "image": public_image_url,
            "attributes": [
                {
                    "trait_type": "Asset Type",
                    "value": request.form.get('category', 'image')
                },
                {
                    "trait_type": "Creation Date",
                    "value": datetime.now().isoformat()
                }
            ]
        }

        metadata_filename = 'metadata.json'
        metadata_path = os.path.join(upload_path, metadata_filename)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        public_metadata_url = f"{base_url}/api/uploads/{timestamp}/{metadata_filename}"

        logger.debug(f"File uploaded successfully. Image URL: {public_image_url}, Metadata URL: {public_metadata_url}")

        return jsonify({
            'message': 'Files uploaded successfully',
            'image_url': f"{base_url}/api/uploads/{relative_image_path}",
            'metadata_url': f"{base_url}/api/uploads/{relative_metadata_path}"
        }), 200

    except Exception as e:
        logger.error(f"Error handling upload: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


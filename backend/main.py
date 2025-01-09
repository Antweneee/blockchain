from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
from config import Config
from models import db
from models.user import User
from models.asset import Asset
from models.listing import Listing
from models.transaction import Transaction
from models.wallet import WalletTransaction
import os
from flask import send_from_directory
from flask import current_app

migrate = Migrate()
sess = Session()
UPLOAD_FOLDER = '/data/uploads'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    CORS(app, 
         resources={r"/api/*": {"origins": app.config.get('CORS_ALLOW_ORIGINS', '*')}},
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    db.init_app(app)
    migrate.init_app(app, db)
    sess.init_app(app)

    from routes.auth import auth_bp
    from routes.marketplace import marketplace_bp
    from routes.users import users_bp
    from routes.wallet import wallet_bp
    from routes.assets import assets_bp
    from routes.upload import upload_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(upload_bp, url_prefix='/upload')

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        app.logger.debug(f"Serving file: {filename} from {UPLOAD_FOLDER}")
        return send_from_directory(UPLOAD_FOLDER, filename)

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({'error': 'Bad request'}), 400

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})

    return app

app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

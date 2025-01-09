import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    db_path = os.getenv('DATABASE_PATH')
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.getenv('SESSION_DIR', '/tmp/flask_session')
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'cryptoplace_session'
    SESSION_REFRESH_EACH_REQUEST = True

    XRPL_NODE = os.getenv('XRPL_NODE', 'wss://s.altnet.rippletest.net:51233')
    
    CORS_HEADERS = 'Content-Type'

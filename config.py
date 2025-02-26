import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration."""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    CSRF_ENABLED = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'hcs.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    
    # QR Code configuration
    QR_CODE_FOLDER = os.path.join('app', 'static', 'qrcodes')
    
    # Payment configuration (mock)
    TELEBIRR_API_KEY = os.environ.get('TELEBIRR_API_KEY') or 'mock-telebirr-key'
    CHAPA_API_KEY = os.environ.get('CHAPA_API_KEY') or 'mock-chapa-key' 
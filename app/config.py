"""
Application Configuration
Centralized configuration for all demos
"""
import os
from datetime import timedelta
from pathlib import Path

# Base directory - module level
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "data" / "agentic_canvas.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_FILE_DIR = BASE_DIR / 'data' / 'sessions'
    
    # SocketIO
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False
    
    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = 'gpt-4'
    OPENAI_TEMPERATURE = 0.7
    
    # Application Settings
    APP_NAME = 'Agentic Canvas'
    APP_VERSION = '1.0.0'
    
    # Demo Configuration
    DEMO_MODE = True
    SIMULATION_ENABLED = True
    SIMULATION_INTERVAL = 1.0
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = BASE_DIR / 'logs' / 'agentic_canvas.log'
    
    # File Upload
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'xlsx', 'json'}
    
    # Export
    EXPORT_FOLDER = BASE_DIR / 'data' / 'exports'
    
    @staticmethod
    def init_app(app):
        """Initialize application-specific configuration"""
        # ✅ FIX: Use module-level BASE_DIR, not Config.BASE_DIR
        data_dir = BASE_DIR / 'data'
        os.makedirs(data_dir, exist_ok=True)
        
        # Create necessary subdirectories
        session_dir = BASE_DIR / 'data' / 'sessions'
        log_dir = BASE_DIR / 'logs'
        upload_dir = BASE_DIR / 'data' / 'uploads'
        export_dir = BASE_DIR / 'data' / 'exports'
        
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(export_dir, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        log_file = BASE_DIR / 'logs' / 'agentic_canvas.log'
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
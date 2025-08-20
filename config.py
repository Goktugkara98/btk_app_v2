"""
Application Configuration Management

This module provides a hybrid configuration system that combines:
- Environment variables for sensitive data (API keys, passwords, secrets)
- Configuration files for application settings (hosts, ports, features)
- Default values for development
- Environment-specific configurations
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _env_bool(name: str, default: bool = False) -> bool:
    """Convert environment variable to boolean."""
    val = os.environ.get(name)
    if val is None:
        return default
    return str(val).lower() in ("true", "1", "t", "yes", "y")

def _env_int(name: str, default: int = 0) -> int:
    """Convert environment variable to integer."""
    val = os.environ.get(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default

class DatabaseConfig:
    """Database configuration settings."""
    
    # Connection settings
    HOST = os.environ.get('DB_HOST', 'localhost')
    PORT = _env_int('DB_PORT', 3306)
    USERNAME = os.environ.get('DB_USERNAME', 'root')
    PASSWORD = os.environ.get('DB_PASSWORD', '')  # Must be set in production
    DATABASE = os.environ.get('DB_NAME', 'btk_app')
    
    # Connection pool settings
    POOL_SIZE = _env_int('DB_POOL_SIZE', 10)
    MAX_OVERFLOW = _env_int('DB_MAX_OVERFLOW', 20)
    POOL_TIMEOUT = _env_int('DB_POOL_TIMEOUT', 30)
    POOL_RECYCLE = _env_int('DB_POOL_RECYCLE', 3600)
    POOL_PRE_PING = _env_bool('DB_POOL_PRE_PING', True)
    
    # Character encoding
    CHARSET = 'utf8mb4'
    COLLATION = 'utf8mb4_unicode_ci'
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary for database connection."""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'username': cls.USERNAME,
            'password': cls.PASSWORD,
            'database': cls.DATABASE,
            'charset': cls.CHARSET,
            'collation': cls.COLLATION,
            'pool_size': cls.POOL_SIZE,
            'max_overflow': cls.MAX_OVERFLOW,
            'pool_timeout': cls.POOL_TIMEOUT,
            'pool_recycle': cls.POOL_RECYCLE,
            'pool_pre_ping': cls.POOL_PRE_PING
        }

class APIConfig:
    """API configuration settings."""
    
    # Gemini AI API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')  # Required for AI features
    GEMINI_API_URL = os.environ.get('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta')
    
    # External APIs (if any)
    EXTERNAL_API_KEY = os.environ.get('EXTERNAL_API_KEY')
    EXTERNAL_API_URL = os.environ.get('EXTERNAL_API_URL')
    
    # Rate limiting
    API_RATE_LIMIT = _env_int('API_RATE_LIMIT', 100)  # requests per minute
    API_RATE_LIMIT_WINDOW = _env_int('API_RATE_LIMIT_WINDOW', 60)  # seconds

class SecurityConfig:
    """Security configuration settings."""
    
    # Flask secret key (must be set in production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    
    # Session settings
    SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_HTTPONLY = _env_bool('SESSION_COOKIE_HTTPONLY', True)
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Password hashing
    PASSWORD_SALT_ROUNDS = _env_int('PASSWORD_SALT_ROUNDS', 12)
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']

class AppConfig:
    """Application configuration settings."""
    
    # Basic app settings
    APP_NAME = 'BTK App'
    APP_VERSION = '2.0.0'
    DEBUG = _env_bool('FLASK_DEBUG', True)
    TESTING = _env_bool('FLASK_TESTING', False)
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    TEMPLATE_DIR = BASE_DIR / 'app' / 'templates'
    STATIC_DIR = BASE_DIR / 'app' / 'static'
    UPLOAD_DIR = BASE_DIR / 'uploads'
    LOG_DIR = BASE_DIR / 'logs'
    
    # Feature flags
    ENABLE_AI_FEATURES = _env_bool('ENABLE_AI_FEATURES', True)
    ENABLE_USER_REGISTRATION = _env_bool('ENABLE_USER_REGISTRATION', True)
    ENABLE_QUIZ_FEATURES = _env_bool('ENABLE_QUIZ_FEATURES', True)
    ENABLE_ADMIN_PANEL = _env_bool('ENABLE_ADMIN_PANEL', True)
    
    # Quiz settings
    QUIZ_TIME_LIMIT = _env_int('QUIZ_TIME_LIMIT', 30)  # minutes
    MAX_QUESTIONS_PER_QUIZ = _env_int('MAX_QUESTIONS_PER_QUIZ', 50)
    QUESTIONS_DIR = os.environ.get('QUESTIONS_DIR', 'app/data/quiz_banks')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        for directory in [cls.UPLOAD_DIR, cls.LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

class Config:
    """Main configuration class that combines all configs."""
    
    # Import all configurations
    DATABASE = DatabaseConfig
    API = APIConfig
    SECURITY = SecurityConfig
    APP = AppConfig
    
    # Legacy compatibility
    SECRET_KEY = SECURITY.SECRET_KEY
    DEBUG = APP.DEBUG
    TESTING = APP.TESTING
    
    @classmethod
    def validate_production_config(cls) -> None:
        """Validate that all required production settings are configured."""
        if not cls.APP.TESTING and not cls.APP.DEBUG:
            # Production environment checks
            required_vars = [
                'SECRET_KEY',
                'DB_PASSWORD',
                'GEMINI_API_KEY'
            ]
            
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            if missing_vars:
                raise ValueError(f"Missing required environment variables for production: {missing_vars}")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    
    # Override database for testing
    DATABASE = type('TestDatabaseConfig', (), {
        'HOST': 'localhost',
        'PORT': 3306,
        'USERNAME': 'test_user',
        'PASSWORD': 'test_password',
        'DATABASE': 'btk_app_test',
        'POOL_SIZE': 5,
        'MAX_OVERFLOW': 10,
        'POOL_TIMEOUT': 10,
        'POOL_RECYCLE': 1800,
        'POOL_PRE_PING': True,
        'CHARSET': 'utf8mb4',
        'COLLATION': 'utf8mb4_unicode_ci'
    })()

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Validate production settings
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.validate_production_config()

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config_map.get(config_name, config_map['default'])
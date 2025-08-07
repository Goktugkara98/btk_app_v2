import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # MySQL database configuration
    MYSQL_CONFIG = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'database': os.environ.get('MYSQL_DB', 'btk_app'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'autocommit': True
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'test_user',
        'password': 'test_password',
        'database': 'btk_app_test',
        'port': 3306,
        'charset': 'utf8mb4',
        'use_unicode': True,
        'autocommit': True
    }


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Ensure required production environment variables are set
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")
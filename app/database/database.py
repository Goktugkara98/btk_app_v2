# =============================================================================
# FLASK-SQLALCHEMY CONFIGURATION
# =============================================================================
# SQLAlchemy database configuration for Flask application
# =============================================================================

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Configure naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# Initialize SQLAlchemy
db = SQLAlchemy(metadata=metadata)

def init_db(app):
    """Initialize database with Flask app"""
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://"
        f"{os.getenv('MYSQL_USER', 'root')}:"
        f"{os.getenv('MYSQL_PASSWORD', '')}@"
        f"{os.getenv('MYSQL_HOST', 'localhost')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DB', 'btk_app')}"
        f"?charset=utf8mb4"
    )
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'echo': os.getenv('FLASK_ENV') == 'development'
    }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app with SQLAlchemy
    db.init_app(app)
    
    return db

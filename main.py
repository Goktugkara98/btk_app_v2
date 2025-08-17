from flask import Flask, session
from config import Config
from app.database.db_connection import DatabaseConnection
from app.database.db_migrations_v2 import DatabaseMigrations
import os
import secrets
import sys

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    template_dir = os.path.abspath('app/templates')
    static_dir = os.path.abspath('app/static')
    app = Flask(__name__, 
               template_folder=template_dir,
               static_folder=static_dir,
               static_url_path='/static')
    app.config.from_object(config_class)
    
    app.secret_key = secrets.token_hex(16)
    app.config['SESSION_TYPE'] = 'filesystem'
    
    os.makedirs(app.instance_path, exist_ok=True)
    
    db_connection = None
    try:
        db_connection = DatabaseConnection()
        migrations = DatabaseMigrations(db_connection)

        # Gated operations per environment flags
        if app.config.get('AUTO_MIGRATE', True):
            migrations.run_migrations()

        if app.config.get('AUTO_SEED_CURR', True):
            # Ensure curriculum seed data is loaded (grades, subjects, units, topics)
            migrations.seed_initial_data()

        if app.config.get('AUTO_CREATE_INDEXES', True):
            # Ensure performance indexes exist (idempotent)
            migrations.create_missing_indexes()

        if app.config.get('AUTO_SEED_USERS', False):
            migrations.seed_default_users()

        if app.config.get('AUTO_SEED_QUESTIONS', True):
            questions_dir = app.config.get('QUESTIONS_DIR', 'app/data/quiz_banks')
            migrations.seed_questions_if_empty(questions_dir)

        app.config['DB_CONNECTION'] = db_connection
        
    except Exception as e:
        if db_connection:
            db_connection.close()
        raise
    
    from app.routes import api_bp, pages_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(pages_bp)
    
    @app.context_processor
    def inject_session():
        return {'session': session}
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
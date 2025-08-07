from flask import Flask, session
from config import Config
from app.database.db_connection import DatabaseConnection
from app.database.db_migrations import DatabaseMigrations
from app.database.quiz_data_loader import QuestionLoader
import os
import secrets

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
        migrations.run_migrations()
        
        question_loader = QuestionLoader(db_connection=db_connection)
        
        with db_connection as conn:
            conn.cursor.execute("SELECT COUNT(*) as count FROM questions")
            question_count = conn.cursor.fetchone()['count']
        
        if question_count == 0:
            question_loader.process_all_question_files()
        
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